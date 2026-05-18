from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
import math

app = Flask(__name__)
app.secret_key = "nutrismart_secret_key_2024"

# ─────────────────────────────────────────
#  DATABASE SETUP
# ─────────────────────────────────────────
def init_db():
    conn = sqlite3.connect('database/diet.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        weight REAL,
        height REAL,
        activity TEXT,
        goal TEXT,
        diet_pref TEXT,
        condition TEXT,
        bmi REAL,
        daily_calories INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS food_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        food_name TEXT,
        calories INTEGER,
        date TEXT DEFAULT (date('now'))
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS water_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        cups INTEGER,
        date TEXT DEFAULT (date('now'))
    )''')

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────
def calculate_bmi(weight, height):
    bmi = weight / ((height / 100) ** 2)
    return round(bmi, 1)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "#3b82f6"
    elif bmi < 25:
        return "Normal Weight ✅", "#16a34a"
    elif bmi < 30:
        return "Overweight ⚠️", "#f59e0b"
    else:
        return "Obese 🚨", "#dc2626"

def calculate_calories(weight, height, age, gender, activity, goal):
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    mul = {'sedentary': 1.2, 'light': 1.375, 'moderate': 1.55, 'active': 1.725}
    cal = bmr * mul.get(activity, 1.2)

    if goal == 'lose':
        cal -= 400
    elif goal in ('gain', 'muscle'):
        cal += 300

    return int(cal)

def get_diet_plan(pref, goal):
    plans = {
        'veg': {
            'lose': [
                {'time': 'Early Morning (6:30 AM)', 'name': 'Warm Lemon Water + Almonds', 'cal': '~50 kcal', 'items': '1 glass warm water + lemon + 5 soaked almonds'},
                {'time': 'Breakfast (8:00 AM)', 'name': 'Oats Upma + Green Tea', 'cal': '~220 kcal', 'items': '1 cup oats upma with veggies + green tea'},
                {'time': 'Mid Morning (11:00 AM)', 'name': 'Seasonal Fruit', 'cal': '~80 kcal', 'items': '1 apple / orange / guava'},
                {'time': 'Lunch (1:00 PM)', 'name': 'Brown Rice + Dal + Sabzi + Salad', 'cal': '~450 kcal', 'items': '1 cup brown rice + dal + sabzi + cucumber salad + buttermilk'},
                {'time': 'Evening Snack (4:30 PM)', 'name': 'Sprouts Chaat + Buttermilk', 'cal': '~150 kcal', 'items': '½ cup mixed sprouts + 1 glass buttermilk'},
                {'time': 'Dinner (7:30 PM)', 'name': '2 Chapati + Sabzi + Curd', 'cal': '~380 kcal', 'items': '2 wheat chapati + vegetable curry + curd'},
                {'time': 'Bedtime (9:30 PM)', 'name': 'Warm Turmeric Milk', 'cal': '~80 kcal', 'items': '1 glass low-fat milk + turmeric'},
            ],
            'maintain': [
                {'time': 'Early Morning (6:30 AM)', 'name': 'Warm Water + Nuts', 'cal': '~80 kcal', 'items': '1 glass warm water + 5 almonds + 2 walnuts'},
                {'time': 'Breakfast (8:00 AM)', 'name': 'Poha + Milk', 'cal': '~320 kcal', 'items': '1.5 cups poha with peas & onion + 1 glass milk'},
                {'time': 'Mid Morning (11:00 AM)', 'name': 'Fruit + Nuts', 'cal': '~130 kcal', 'items': '1 banana + handful peanuts'},
                {'time': 'Lunch (1:00 PM)', 'name': 'Rice + Dal + Sabzi + Roti', 'cal': '~550 kcal', 'items': '1 cup rice + dal + sabzi + 1 roti + salad + curd'},
                {'time': 'Evening Snack (4:30 PM)', 'name': 'Snack + Chai', 'cal': '~200 kcal', 'items': '1-2 baked snacks + 1 cup tea'},
                {'time': 'Dinner (7:30 PM)', 'name': '3 Roti + Paneer/Dal + Curd', 'cal': '~500 kcal', 'items': '3 rotis + paneer or dal curry + curd + salad'},
                {'time': 'Bedtime (9:30 PM)', 'name': 'Milk + Banana', 'cal': '~200 kcal', 'items': '1 glass full-fat milk + 1 banana'},
            ],
            'gain': [
                {'time': 'Early Morning (6:30 AM)', 'name': 'Banana Shake + Dates', 'cal': '~250 kcal', 'items': '2 bananas + milk shake + 4 soaked dates'},
                {'time': 'Breakfast (8:00 AM)', 'name': 'Puri + Sabzi + Curd', 'cal': '~500 kcal', 'items': '3-4 puris + potato sabzi + curd + milk'},
                {'time': 'Mid Morning (11:00 AM)', 'name': 'Peanut Butter Toast + Juice', 'cal': '~300 kcal', 'items': '2 brown bread + peanut butter + juice'},
                {'time': 'Lunch (1:00 PM)', 'name': 'Full Thali', 'cal': '~700 kcal', 'items': '2 cups rice + 2 rotis + 2 sabzis + dal + curd + salad'},
                {'time': 'Evening Snack (4:30 PM)', 'name': 'Chana Chaat + Lassi', 'cal': '~350 kcal', 'items': '1 cup boiled chana + sweet lassi'},
                {'time': 'Dinner (7:30 PM)', 'name': '4 Roti + Paneer Curry + Rice', 'cal': '~650 kcal', 'items': '4 rotis + rich paneer curry + ½ cup rice + curd'},
                {'time': 'Bedtime (9:30 PM)', 'name': 'Full Fat Milk + Dry Fruits', 'cal': '~300 kcal', 'items': '1 glass full-fat milk + mixed dry fruits'},
            ],
        },
        'nonveg': {
            'lose': [
                {'time': 'Early Morning (6:30 AM)', 'name': 'Warm Lemon Water + Almonds', 'cal': '~50 kcal', 'items': '1 glass warm water with lemon + 5 soaked almonds'},
                {'time': 'Breakfast (8:00 AM)', 'name': 'Egg White Omelette + Brown Bread', 'cal': '~250 kcal', 'items': '3 egg whites omelette + 2 brown bread + green tea'},
                {'time': 'Mid Morning (11:00 AM)', 'name': 'Fruit', 'cal': '~70 kcal', 'items': '1 medium apple or orange'},
                {'time': 'Lunch (1:00 PM)', 'name': 'Grilled Chicken + Brown Rice + Salad', 'cal': '~480 kcal', 'items': '100g grilled chicken + 1 cup brown rice + salad + buttermilk'},
                {'time': 'Evening Snack (4:30 PM)', 'name': 'Boiled Egg + Sprouts', 'cal': '~160 kcal', 'items': '1 boiled egg + ½ cup mixed sprouts'},
                {'time': 'Dinner (7:30 PM)', 'name': 'Fish Curry + 2 Roti + Sabzi', 'cal': '~420 kcal', 'items': '100g fish curry + 2 wheat rotis + green vegetable'},
                {'time': 'Bedtime (9:30 PM)', 'name': 'Warm Turmeric Milk', 'cal': '~80 kcal', 'items': '1 glass low-fat milk + turmeric'},
            ],
            'maintain': [
                {'time': 'Early Morning (6:30 AM)', 'name': 'Warm Water + Nuts', 'cal': '~80 kcal', 'items': '1 glass warm water + almonds + walnuts'},
                {'time': 'Breakfast (8:00 AM)', 'name': 'Egg Bhurji + Roti + Milk', 'cal': '~380 kcal', 'items': '2 eggs bhurji + 2 rotis + 1 glass milk'},
                {'time': 'Mid Morning (11:00 AM)', 'name': 'Fruit + Nuts', 'cal': '~130 kcal', 'items': '1 banana + peanuts'},
                {'time': 'Lunch (1:00 PM)', 'name': 'Chicken Rice + Dal + Salad', 'cal': '~580 kcal', 'items': '1 cup rice + chicken curry + dal + salad + curd'},
                {'time': 'Evening Snack (4:30 PM)', 'name': 'Boiled Eggs + Tea', 'cal': '~170 kcal', 'items': '2 boiled eggs + 1 cup tea'},
                {'time': 'Dinner (7:30 PM)', 'name': '3 Roti + Chicken/Mutton Curry', 'cal': '~550 kcal', 'items': '3 wheat rotis + chicken or mutton curry + salad'},
                {'time': 'Bedtime (9:30 PM)', 'name': 'Milk', 'cal': '~150 kcal', 'items': '1 glass full-fat milk'},
            ],
            'gain': [
                {'time': 'Early Morning (6:30 AM)', 'name': 'Banana Shake + Eggs', 'cal': '~350 kcal', 'items': 'Banana milk shake + 2 boiled eggs'},
                {'time': 'Breakfast (8:00 AM)', 'name': 'Chicken Sandwich + Juice', 'cal': '~500 kcal', 'items': 'Chicken sandwich + juice + milk'},
                {'time': 'Mid Morning (11:00 AM)', 'name': 'Dry Fruits + Yoghurt', 'cal': '~280 kcal', 'items': 'Mixed dry fruits + full-fat yoghurt'},
                {'time': 'Lunch (1:00 PM)', 'name': 'Rice + Chicken + Egg + Dal', 'cal': '~750 kcal', 'items': '2 cups rice + chicken curry + fried egg + dal + salad'},
                {'time': 'Evening Snack (4:30 PM)', 'name': 'Protein Shake / Kebab', 'cal': '~380 kcal', 'items': 'Protein shake or mutton seekh kebab'},
                {'time': 'Dinner (7:30 PM)', 'name': '4 Roti + Mutton Curry + Rice', 'cal': '~700 kcal', 'items': '4 rotis + rich mutton curry + ½ cup rice + curd'},
                {'time': 'Bedtime (9:30 PM)', 'name': 'Milk + Peanut Butter', 'cal': '~300 kcal', 'items': '1 glass full-fat milk + 2 tbsp peanut butter'},
            ],
        }
    }
    pref_key = 'veg' if pref == 'vegan' else pref
    goal_key = 'gain' if goal == 'muscle' else goal
    return plans.get(pref_key, plans['veg']).get(goal_key, plans['veg']['maintain'])

def get_avoid_foods(goal):
    avoid = {
        'lose': ['Fried foods (samosa, chips, fries)', 'Sugary drinks (cold drinks)', 'White bread & maida items', 'Full-fat dairy in excess', 'Processed & packaged foods', 'Late night heavy meals'],
        'maintain': ['Excessive junk food', 'Too much sugar & sweets', 'Skipping meals', 'Overeating at one time', 'Processed foods'],
        'gain': ['Empty calorie foods', 'Skipping meals', 'Drinking water before meals', 'Crash diets', 'Excessive cardio without strength training'],
        'muscle': ['Alcohol', 'Sugary foods', 'Trans fats', 'Skipping post-workout meals', 'Insufficient sleep'],
    }
    return avoid.get(goal, avoid['maintain'])

# ─────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        name     = request.form['name']
        age      = int(request.form['age'])
        gender   = request.form['gender']
        weight   = float(request.form['weight'])
        height   = float(request.form['height'])
        activity = request.form['activity']
        goal     = request.form['goal']
        pref     = request.form['diet_pref']
        cond     = request.form['condition']

        bmi      = calculate_bmi(weight, height)
        cal      = calculate_calories(weight, height, age, gender, activity, goal)
        category, color = bmi_category(bmi)

        # Save to DB
        os.makedirs('database', exist_ok=True)
        conn = sqlite3.connect('database/diet.db')
        c = conn.cursor()
        c.execute('''INSERT INTO users (name,age,gender,weight,height,activity,goal,diet_pref,condition,bmi,daily_calories)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                  (name, age, gender, weight, height, activity, goal, pref, cond, bmi, cal))
        user_id = c.lastrowid
        conn.commit()
        conn.close()

        session['user_id'] = user_id
        session['user_name'] = name
        session['bmi'] = bmi
        session['bmi_category'] = category
        session['bmi_color'] = color
        session['daily_calories'] = cal
        session['goal'] = goal
        session['diet_pref'] = pref

        return redirect(url_for('diet_plan'))

    return render_template('profile.html')

@app.route('/diet-plan')
def diet_plan():
    if 'user_id' not in session:
        return redirect(url_for('profile'))

    goal = session.get('goal', 'maintain')
    pref = session.get('diet_pref', 'veg')
    meals = get_diet_plan(pref, goal)
    avoid = get_avoid_foods(goal)

    goal_label = {'lose': 'Weight Loss 🔻', 'maintain': 'Maintain Weight ⚖️', 'gain': 'Weight Gain 🔺', 'muscle': 'Build Muscle 💪'}.get(goal, goal)
    pref_label = {'veg': 'Vegetarian 🥦', 'nonveg': 'Non-Vegetarian 🍗', 'vegan': 'Vegan 🌱'}.get(pref, pref)

    return render_template('diet_plan.html',
        meals=meals, avoid=avoid,
        name=session.get('user_name'),
        bmi=session.get('bmi'),
        bmi_category=session.get('bmi_category'),
        bmi_color=session.get('bmi_color'),
        daily_calories=session.get('daily_calories'),
        goal_label=goal_label,
        pref_label=pref_label
    )

@app.route('/tracker')
def tracker():
    if 'user_id' not in session:
        return redirect(url_for('profile'))

    user_id = session['user_id']
    conn = sqlite3.connect('database/diet.db')
    c = conn.cursor()
    c.execute("SELECT food_name, calories, id FROM food_log WHERE user_id=? AND date=date('now')", (user_id,))
    food_items = c.fetchall()
    c.execute("SELECT cups FROM water_log WHERE user_id=? AND date=date('now')", (user_id,))
    water_row = c.fetchone()
    conn.close()

    consumed = sum(f[1] for f in food_items)
    target = session.get('daily_calories', 2000)
    remaining = max(0, target - consumed)
    pct = min(100, int((consumed / target) * 100)) if target else 0
    water_cups = water_row[0] if water_row else 0

    return render_template('tracker.html',
        food_items=food_items,
        consumed=consumed,
        target=target,
        remaining=remaining,
        pct=pct,
        water_cups=water_cups,
        name=session.get('user_name', 'User')
    )

@app.route('/add-food', methods=['POST'])
def add_food():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 403
    data = request.get_json()
    food_name = data.get('food_name')
    calories  = int(data.get('calories', 0))
    conn = sqlite3.connect('database/diet.db')
    c = conn.cursor()
    c.execute("INSERT INTO food_log (user_id, food_name, calories) VALUES (?,?,?)",
              (session['user_id'], food_name, calories))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/delete-food/<int:food_id>', methods=['POST'])
def delete_food(food_id):
    conn = sqlite3.connect('database/diet.db')
    c = conn.cursor()
    c.execute("DELETE FROM food_log WHERE id=?", (food_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/update-water', methods=['POST'])
def update_water():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 403
    data = request.get_json()
    cups = int(data.get('cups', 0))
    conn = sqlite3.connect('database/diet.db')
    c = conn.cursor()
    c.execute("SELECT id FROM water_log WHERE user_id=? AND date=date('now')", (session['user_id'],))
    row = c.fetchone()
    if row:
        c.execute("UPDATE water_log SET cups=? WHERE id=?", (cups, row[0]))
    else:
        c.execute("INSERT INTO water_log (user_id, cups) VALUES (?,?)", (session['user_id'], cups))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/tips')
def tips():
    return render_template('tips.html')

if __name__ == '__main__':
    os.makedirs('database', exist_ok=True)
    init_db()
    app.run(debug=True)
