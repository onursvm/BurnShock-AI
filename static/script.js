// Çok Dilli Sözlük (TR & EN Translations)
const translations = {
  tr: {
    tagline: "Fast Food & Cheat Meal Workout Shock Classifier",
    formTitle: "Öğün ve Tüketici Bilgileri",
    formSubtitle: "Yediğiniz veya planladığınız cheat meal detaylarını girin",
    presetTitle: "Örnek Senaryo Yükle:",
    presetBurger: "🍔 Double Burger Binge",
    presetPizza: "🍕 Pizza Feast",
    presetLight: "🥗 Dengeli / Hafif",
    secGeneral: "Genel Tercihler",
    lblChain: "Restoran Zinciri",
    lblMeal: "Menü / Öğün Türü",
    lblGender: "Cinsiyet",
    lblFitness: "Fitness / Egzersiz Seviyesi",
    catDessert: "Tatlı Bombası & Büyük Shake",
    catBurger: "Double Burger & Büyük Boy Patates",
    catChicken: "Kızarmış Tavuk Kovası & Salata",
    catLateNight: "Gece Ekonomik Menü Tıkınması",
    catBurrito: "Dolu Burrito, Nachos & Gazlı İçecek",
    catPizza: "Pizza Ziyafeti & Peynirli Ekmek",
    genderMale: "Erkek",
    genderFemale: "Kadın",
    fitSedentary: "Hareketsiz (Sedanter)",
    fitModerate: "Orta Düzey Aktif",
    fitHigh: "İleri Düzey Antrenmanlı",
    secNutrients: "Besin Değerleri & Kalori",
    lblCalories: "Toplam Kalori (kcal)",
    lblItemCount: "Ürün / Porsiyon Adedi",
    lblCarbs: "Karbonhidrat (gr)",
    lblSugar: "Şeker (gr)",
    lblProtein: "Protein (gr)",
    lblFat: "Toplam Yağ (gr)",
    lblSatFat: "Doymuş Yağ (gr)",
    lblSodium: "Sodyum (mg)",
    secPhysical: "Fiziksel Bilgiler",
    lblAge: "Yaş",
    lblWeight: "Kilo (kg)",
    btnCalculate: "Antrenman Şokunu Hesapla",
    btnCalculating: "Hesaplanıyor...",
    emptyTitle: "Tahmin Bekleniyor",
    emptyDesc: "Soldaki parametreleri doldurup \"Antrenman Şokunu Hesapla\" butonuna basın. Yapay zeka modelimiz yakım ihtiyacınızı sınıflandırsın.",
    lblConfidence: "Güven Oranı:",
    coachAdvice: "Antrenör Tavsiyesi",
    probTitle: "Sınıf Olasılık Dağılımı"
  },
  en: {
    tagline: "Fast Food & Cheat Meal Workout Shock Classifier",
    formTitle: "Meal & Consumer Profile",
    formSubtitle: "Enter the details of your cheat meal or planned binge",
    presetTitle: "Load Sample Scenario:",
    presetBurger: "🍔 Double Burger Binge",
    presetPizza: "🍕 Pizza Feast",
    presetLight: "🥗 Balanced / Light",
    secGeneral: "General Choices",
    lblChain: "Fast Food Chain",
    lblMeal: "Meal Category",
    lblGender: "Gender",
    lblFitness: "Fitness / Activity Level",
    catDessert: "Dessert Overload & Large Shake",
    catBurger: "Double Burger & Large Fry",
    catChicken: "Fried Chicken Bucket & Slaw",
    catLateNight: "Late-Night Value Menu Binge",
    catBurrito: "Loaded Burrito, Nachos & Soda",
    catPizza: "Pizza Feast & Cheesy Bread",
    genderMale: "Male",
    genderFemale: "Female",
    fitSedentary: "Sedentary",
    fitModerate: "Moderately Active",
    fitHigh: "Highly Trained",
    secNutrients: "Nutritional Values & Calories",
    lblCalories: "Total Calories (kcal)",
    lblItemCount: "Item Count / Servings",
    lblCarbs: "Carbohydrates (g)",
    lblSugar: "Sugar (g)",
    lblProtein: "Protein (g)",
    lblFat: "Total Fat (g)",
    lblSatFat: "Saturated Fat (g)",
    lblSodium: "Sodium (mg)",
    secPhysical: "Physical Profile",
    lblAge: "Age",
    lblWeight: "Weight (kg)",
    btnCalculate: "Calculate Workout Shock",
    btnCalculating: "Calculating...",
    emptyTitle: "Awaiting Prediction",
    emptyDesc: "Fill in the meal parameters on the left and click \"Calculate Workout Shock\" to evaluate burn requirements.",
    lblConfidence: "Confidence Score:",
    coachAdvice: "Coach Recommendation",
    probTitle: "Class Probability Distribution"
  }
};

let currentLang = 'tr';
let lastPredictionData = null;

// Dil değiştirme ve kayan buton animasyonu
function setLanguage(lang) {
  currentLang = lang;
  const track = document.getElementById('langSwitch');
  const btnTR = document.getElementById('btnTR');
  const btnEN = document.getElementById('btnEN');

  if (lang === 'en') {
    track.classList.add('en-active');
    btnEN.classList.add('active');
    btnTR.classList.remove('active');
  } else {
    track.classList.remove('en-active');
    btnTR.classList.add('active');
    btnEN.classList.remove('active');
  }

  // Arayüz metinlerini güncelle
  const dict = translations[lang];
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });

  // Eğer ekranda tahmin sonucu varsa dili hemen güncelle
  if (lastPredictionData) {
    displayResults(lastPredictionData);
  }
}

// Hazır Senaryolar (Presets)
const presets = {
  burger: {
    fast_food_chain: "Five Guys",
    meal_category: "Double Burger & Large Fry",
    consumer_gender: "Male",
    fitness_level: "Sedentary",
    total_calories: 2200,
    item_count: 4,
    carb_grams: 210,
    sugar_grams: 80,
    protein_grams: 65,
    fat_grams: 110,
    saturated_fat_grams: 45,
    sodium_mg: 3400,
    consumer_age: 28,
    consumer_weight_kg: 84
  },
  pizza: {
    fast_food_chain: "Domino's Pizza",
    meal_category: "Pizza Feast & Cheesy Bread",
    consumer_gender: "Male",
    fitness_level: "Moderately Active",
    total_calories: 1850,
    item_count: 3,
    carb_grams: 190,
    sugar_grams: 45,
    protein_grams: 70,
    fat_grams: 85,
    saturated_fat_grams: 38,
    sodium_mg: 2800,
    consumer_age: 26,
    consumer_weight_kg: 76
  },
  light: {
    fast_food_chain: "Subway",
    meal_category: "Late-Night Value Menu Binge",
    consumer_gender: "Female",
    fitness_level: "Highly Trained",
    total_calories: 850,
    item_count: 2,
    carb_grams: 95,
    sugar_grams: 20,
    protein_grams: 40,
    fat_grams: 30,
    saturated_fat_grams: 10,
    sodium_mg: 1200,
    consumer_age: 24,
    consumer_weight_kg: 60
  }
};

function applyPreset(name) {
  const data = presets[name];
  if (!data) return;

  for (const [key, value] of Object.entries(data)) {
    const el = document.getElementById(key);
    if (el) {
      el.value = value;
    }
  }
}

// Form Gönderimi ve API Çağrısı
document.getElementById('predictionForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const submitBtn = document.getElementById('submitBtn');
  const btnText = submitBtn.querySelector('.btn-text');
  const spinner = submitBtn.querySelector('.spinner');

  btnText.style.display = 'none';
  spinner.style.display = 'inline-block';
  submitBtn.disabled = true;

  const formData = new FormData(this);
  const payload = {};
  formData.forEach((value, key) => {
    const num = Number(value);
    payload[key] = isNaN(num) ? value : num;
  });

  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(currentLang === 'tr' ? 'Tahmin alınırken bir hata oluştu' : 'Failed to fetch prediction');
    }

    const data = await response.json();
    lastPredictionData = data;
    displayResults(data);
  } catch (error) {
    alert(error.message);
  } finally {
    btnText.style.display = 'inline-block';
    spinner.style.display = 'none';
    submitBtn.disabled = false;
  }
});

function displayResults(data) {
  const emptyState = document.getElementById('emptyState');
  const resultBox = document.getElementById('resultBox');

  emptyState.style.display = 'none';
  resultBox.style.display = 'block';

  const details = data.details;
  const isTR = currentLang === 'tr';

  const shockBadge = document.getElementById('shockBadge');
  shockBadge.textContent = isTR ? (details.badge_tr || 'Tahmin') : (details.badge_en || 'Prediction');
  shockBadge.style.color = details.color || '#fff';
  shockBadge.style.backgroundColor = details.bg_color || 'rgba(255,255,255,0.1)';

  document.getElementById('confidenceVal').textContent = `%${data.confidence}`;
  
  const title = isTR ? details.title_tr : details.title_en;
  document.getElementById('shockTitle').textContent = title || data.predicted_class;
  document.getElementById('shockTitle').style.color = details.color || '#fff';
  
  document.getElementById('shockDesc').textContent = isTR ? details.description_tr : details.description_en;
  document.getElementById('shockSuggestion').textContent = isTR ? details.suggestion_tr : details.suggestion_en;

  // Olasılık Dağılım Listesi
  const probList = document.getElementById('probList');
  probList.innerHTML = '';

  data.probabilities.forEach(item => {
    const div = document.createElement('div');
    div.className = 'prob-item';
    const displayName = isTR ? item.display_name_tr : item.display_name_en;
    div.innerHTML = `
      <div class="prob-header">
        <span>${displayName}</span>
        <span>%${item.probability}</span>
      </div>
      <div class="prob-bar-bg">
        <div class="prob-bar-fill" style="width: ${item.probability}%; background-color: ${item.color};"></div>
      </div>
    `;
    probList.appendChild(div);
  });
}
