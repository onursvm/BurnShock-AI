import os
import json
import torch
import torch.nn as nn
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# --- PyTorch Model Mimarisi ---
class FoodClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear_layer_stack = nn.Sequential(
            nn.Linear(30, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 4)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear_layer_stack(x)

# Model ağırlıklarını yükleme
device = torch.device("cpu")
model = FoodClassifier()
MODEL_PATH = os.path.join(os.path.dirname(__file__), "food_model.pth")
if os.path.exists(MODEL_PATH):
    state_dict = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()
    print("PyTorch modeli başarıyla yüklendi!")
else:
    print(f"Uyarı: {MODEL_PATH} bulunamadı!")

# --- Veri Ön İşleme Parametreleri ---
# Eğitimde kullanılan One-Hot Kategorileri (toplam 20 sütun)
CATEGORIES = {
    "fast_food_chain": [
        "Burger King", "Domino's Pizza", "Five Guys", "KFC",
        "McDonald's", "Starbucks", "Subway", "Taco Bell", "Wendy's"
    ],
    "meal_category": [
        "Dessert Overload & Large Shake",
        "Double Burger & Large Fry",
        "Fried Chicken Bucket & Slaw",
        "Late-Night Value Menu Binge",
        "Loaded Burrito, Nachos & Soda",
        "Pizza Feast & Cheesy Bread"
    ],
    "consumer_gender": ["Female", "Male"],
    "fitness_level": ["Highly Trained", "Moderately Active", "Sedentary"]
}

# Eğitimde kullanılan Sayısal Sütunlar ve StandardScaler (mean, scale) değerleri (10 sütun)
# 20 + 10 = 30 giriş boyutu
NUMERICAL_COLS = [
    "item_count", "total_calories", "fat_grams", "saturated_fat_grams",
    "carb_grams", "sugar_grams", "protein_grams", "sodium_mg",
    "consumer_age", "consumer_weight_kg"
]

SCALER_PARAMS = {
    "item_count": {"mean": 3.500, "scale": 1.119},
    "total_calories": {"mean": 1598.22, "scale": 670.85},
    "fat_grams": {"mean": 79.85, "scale": 34.26},
    "saturated_fat_grams": {"mean": 31.90, "scale": 14.35},
    "carb_grams": {"mean": 165.44, "scale": 70.73},
    "sugar_grams": {"mean": 62.16, "scale": 31.89},
    "protein_grams": {"mean": 54.03, "scale": 30.58},
    "sodium_mg": {"mean": 2390.49, "scale": 1070.94},
    "consumer_age": {"mean": 41.53, "scale": 13.93},
    "consumer_weight_kg": {"mean": 77.71, "scale": 13.87}
}

# Çıktı Sınıfları (workout_shock_tier)
CLASSES = [
    "Extreme / Half-Marathon Toll",
    "High Sweat Penalty",
    "Moderate Burn",
    "Severe Cardio Deficit"
]

CLASS_DETAILS = {
    "Extreme / Half-Marathon Toll": {
        "title_tr": "Aşırı Şok Seviyesi (Yarı Maraton Eforu)",
        "title_en": "Extreme / Half-Marathon Toll",
        "badge_tr": "Kritik Yük",
        "badge_en": "Critical Load",
        "color": "#ef4444",
        "bg_color": "rgba(239, 68, 68, 0.15)",
        "description_tr": "Alınan kalori ve sodyum miktarı vücut kapasitesini aşırı derecede zorluyor. Bu kaloriyi yakmak için yarı maraton eşdeğeri yüksek yoğunluklu uzun süreli antrenman gerekir.",
        "description_en": "The caloric and sodium surplus pushes the body's limits. Burning this meal requires long-duration, high-intensity endurance training equivalent to a half-marathon.",
        "suggestion_tr": "Bol su tüketin, sindirim için hafif yürüyüşle başlayın ve ertesi gün düşük sodyumlu beslenin.",
        "suggestion_en": "Stay well-hydrated, start with light walking for digestion, and prioritize a low-sodium, clean diet the next day."
    },
    "High Sweat Penalty": {
        "title_tr": "Yüksek Terleme Cezası",
        "title_en": "High Sweat Penalty",
        "badge_tr": "Yüksek Şok",
        "badge_en": "High Shock",
        "color": "#f97316",
        "bg_color": "rgba(249, 115, 22, 0.15)",
        "description_tr": "Önemli düzeyde kalori fazlalığı mevcut. Kalp atışını yükseltecek yoğun kardiyo veya 60-75 dakikalık HIIT antrenmanı gerektirir.",
        "description_en": "Significant caloric surplus detected. Requires rigorous cardiovascular training or a 60-75 minute high-intensity interval session.",
        "suggestion_tr": "Ertesi gün 45-60 dk tempolu koşu veya bisiklet egzersizi önerilir.",
        "suggestion_en": "45-60 minutes of brisk running, rowing, or stationary cycling is strongly advised."
    },
    "Moderate Burn": {
        "title_tr": "Orta Düzey Yakım",
        "title_en": "Moderate Burn",
        "badge_tr": "Dengeli",
        "badge_en": "Balanced",
        "color": "#10b981",
        "bg_color": "rgba(16, 185, 129, 0.15)",
        "description_tr": "Öğün kontrollü bir cheat meal niteliğinde. Standart bir günlük antrenman rutini veya tempolu yürüyüşle kolayca dengelenebilir.",
        "description_en": "A manageable cheat meal. Can be offset with your standard daily workout routine or a brisk walking session.",
        "suggestion_tr": "Günlük 40 dakikalık standart antrenman veya 8.000 adım ile dengelenebilir.",
        "suggestion_en": "Easily balanced with 40 minutes of regular weight training or hitting 8,000 brisk steps."
    },
    "Severe Cardio Deficit": {
        "title_tr": "Ciddi Kardiyo Açığı",
        "title_en": "Severe Cardio Deficit",
        "badge_tr": "Ağır Kardiyo",
        "badge_en": "Severe Deficit",
        "color": "#a855f7",
        "bg_color": "rgba(168, 85, 247, 0.15)",
        "description_tr": "Karbonhidrat ve yağ oranı yüksek bir besin alımı. Standart metabolizma hızının üzerinde kardiyo deficit oluşturulması önerilir.",
        "description_en": "Excessive intake of dense carbs and fats. An intentional caloric burn deficit via cardiovascular workouts is required.",
        "suggestion_tr": "Kademeli olarak HIIT ve intervalli kardiyo ile birkaç güne yayarak dengeleyin.",
        "suggestion_en": "Spread interval cardio and HIIT sessions across the next 2-3 days to maintain metabolic balance."
    }
}

app = FastAPI(title="Fast Food & Cheat Meal Workout Shock Classifier")

# Şablon ve statik dosyalar
templates = Jinja2Templates(directory="templates")
if not os.path.exists("static"):
    os.makedirs("static", exist_ok=True)
if not os.path.exists("templates"):
    os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class MealInput(BaseModel):
    fast_food_chain: str
    meal_category: str
    consumer_gender: str
    fitness_level: str
    item_count: float = Field(default=3.0, ge=1, le=10)
    total_calories: float = Field(default=1500.0, ge=100, le=5000)
    fat_grams: float = Field(default=70.0, ge=0, le=250)
    saturated_fat_grams: float = Field(default=25.0, ge=0, le=100)
    carb_grams: float = Field(default=150.0, ge=0, le=400)
    sugar_grams: float = Field(default=50.0, ge=0, le=250)
    protein_grams: float = Field(default=45.0, ge=0, le=200)
    sodium_mg: float = Field(default=2200.0, ge=100, le=7000)
    consumer_age: float = Field(default=28.0, ge=14, le=90)
    consumer_weight_kg: float = Field(default=75.0, ge=35, le=180)

def preprocess_features(data: MealInput) -> torch.Tensor:
    feature_vector = []

    # 1. One-hot encoding (20 boyut)
    for col, possible_values in CATEGORIES.items():
        user_val = getattr(data, col)
        for cat in possible_values:
            feature_vector.append(1.0 if user_val == cat else 0.0)

    # 2. Standard scaling (10 boyut)
    for col in NUMERICAL_COLS:
        raw_val = float(getattr(data, col))
        mean = SCALER_PARAMS[col]["mean"]
        scale = SCALER_PARAMS[col]["scale"]
        scaled_val = (raw_val - mean) / scale
        feature_vector.append(scaled_val)

    return torch.tensor([feature_vector], dtype=torch.float32)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"categories": CATEGORIES}
    )

@app.post("/api/predict")
async def predict(data: MealInput):
    tensor_input = preprocess_features(data)

    with torch.inference_mode():
        logits = model(tensor_input)
        probabilities = torch.softmax(logits, dim=1).squeeze().tolist()
        pred_idx = int(np.argmax(probabilities))

    predicted_class = CLASSES[pred_idx]
    detail = CLASS_DETAILS.get(predicted_class, {})

    all_probabilities = [
        {
            "class_name": cls,
            "display_name_tr": CLASS_DETAILS[cls]["title_tr"],
            "display_name_en": CLASS_DETAILS[cls]["title_en"],
            "probability": round(prob * 100, 1),
            "color": CLASS_DETAILS[cls]["color"]
        }
        for cls, prob in zip(CLASSES, probabilities)
    ]
    all_probabilities.sort(key=lambda x: x["probability"], reverse=True)

    return JSONResponse({
        "status": "success",
        "predicted_class": predicted_class,
        "confidence": round(probabilities[pred_idx] * 100, 1),
        "details": detail,
        "probabilities": all_probabilities
    })
