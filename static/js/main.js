// ─────────────────────────────────────────
//  NUTRISMART – main.js
// ─────────────────────────────────────────

// TOAST NOTIFICATION
function showToast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}

// ─────────────────────────────────────────
//  FOOD TRACKER
// ─────────────────────────────────────────
function addFood() {
  const nameEl = document.getElementById('foodName');
  const calEl  = document.getElementById('foodCal');
  const name = nameEl.value.trim();
  const cal  = parseInt(calEl.value);

  if (!name || !cal || cal <= 0) {
    showToast('⚠️ Please enter food name and calories!');
    return;
  }

  fetch('/add-food', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ food_name: name, calories: cal })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      nameEl.value = '';
      calEl.value  = '';
      showToast('✅ ' + name + ' added (' + cal + ' kcal)');
      setTimeout(() => location.reload(), 800);
    }
  });
}

function quickAdd(name, cal) {
  fetch('/add-food', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ food_name: name, calories: cal })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast('✅ ' + name + ' added (' + cal + ' kcal)');
      setTimeout(() => location.reload(), 800);
    }
  });
}

function deleteFood(id) {
  fetch('/delete-food/' + id, { method: 'POST' })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast('🗑 Food removed!');
      setTimeout(() => location.reload(), 600);
    }
  });
}

// ─────────────────────────────────────────
//  WATER TRACKER
// ─────────────────────────────────────────
let waterCount = parseInt(document.getElementById('waterCount')?.value || '0');

function buildWater() {
  const div = document.getElementById('waterCups');
  if (!div) return;
  div.innerHTML = '';
  for (let i = 0; i < 8; i++) {
    const btn = document.createElement('button');
    btn.className = 'cup' + (i < waterCount ? ' filled' : '');
    btn.textContent = i < waterCount ? '💧' : '🫙';
    btn.onclick = () => toggleCup(i);
    div.appendChild(btn);
  }
  const txt = document.getElementById('waterText');
  if (txt) txt.textContent = waterCount + ' / 8 cups drank today 💧';
}

function toggleCup(i) {
  waterCount = (i < waterCount) ? i : i + 1;
  buildWater();
  saveWater();
  if (waterCount === 8) showToast('🎉 Water goal reached! Great job!');
}

function resetWater() {
  waterCount = 0;
  buildWater();
  saveWater();
  showToast('💧 Water tracker reset!');
}

function saveWater() {
  fetch('/update-water', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cups: waterCount })
  });
}

// ─────────────────────────────────────────
//  INIT
// ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  buildWater();

  // Keyboard enter on food inputs
  const foodCal = document.getElementById('foodCal');
  if (foodCal) {
    foodCal.addEventListener('keydown', e => {
      if (e.key === 'Enter') addFood();
    });
  }
});
