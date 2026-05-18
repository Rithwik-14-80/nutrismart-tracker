# 🥗 NutriSmart – Smart Diet Planner
### Diploma Final Year Project | CSE | By M. Thirumal Reddy

---

## 📁 Project Structure

```
smart-diet-planner/
│
├── app.py                  ← Python Flask Backend
├── requirements.txt        ← Python packages list
├── README.md               ← This file
│
├── templates/              ← HTML Pages
│   ├── base.html           ← Common layout (nav, footer)
│   ├── index.html          ← Home page
│   ├── profile.html        ← User profile & BMI form
│   ├── diet_plan.html      ← Personalized diet plan
│   ├── tracker.html        ← Calorie & water tracker
│   └── tips.html           ← Health tips page
│
├── static/
│   ├── css/
│   │   └── style.css       ← All styling (CSS)
│   └── js/
│       └── main.js         ← JavaScript (tracker logic)
│
└── database/
    └── diet.db             ← SQLite database (auto-created)
```

---

## ⚙️ How to Run the Project (Step by Step)

### Step 1 – Install Python
- Download Python from https://python.org
- During install, ✅ check "Add Python to PATH"

### Step 2 – Open VS Code
- Open VS Code
- File → Open Folder → Select the `smart-diet-planner` folder

### Step 3 – Open Terminal in VS Code
- Press `Ctrl + `` ` (backtick) to open terminal

### Step 4 – Install Flask
Type this in terminal and press Enter:
```
pip install flask
```

### Step 5 – Run the Project
Type this in terminal:
```
python app.py
```

### Step 6 – Open in Browser
- Open Chrome or any browser
- Go to: http://127.0.0.1:5000
- Your project is LIVE! 🎉

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| BMI Calculator | Calculates BMI from weight & height |
| Calorie Calculator | Uses Mifflin-St Jeor formula |
| Personalized Diet Plan | Based on goal & diet preference |
| Calorie Tracker | Log daily meals with calories |
| Water Tracker | Track 8 cups/day goal |
| Health Tips | 10 science-backed tips |
| SQLite Database | Saves user data permanently |

---

## 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Backend logic |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Page structure |
| CSS3 | Styling & design |
| JavaScript | Dynamic interactions |
| Jinja2 | HTML templating |

---

## 👨‍💻 Developer
**M. Thirumal Reddy**
Diploma Final Year – Computer Science Engineering
