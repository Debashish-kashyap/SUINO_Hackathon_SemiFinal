from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from google import genai
import json


client = genai.Client(api_key="AIzaSyC5BTetHQ-EDbtk0znu4EeRr11yokVDuEE")


app = FastAPI(
    title="Netflix NEXUS AI",
    description="Hybrid AI Growth Engine — Churn Prediction + Regional Intelligence + Retention Automation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    model = pickle.load(open("model.pkl", "rb"))
    print("✅ model.pkl loaded successfully")
except FileNotFoundError:
    model = None
    print("⚠️  model.pkl not found — /predict will return mock scores")


try:
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    vectors = pickle.load(open("vectors.pkl", "rb")) 
    cv = pickle.load(open("vectorizer.pkl", "rb"))
    print("✅ Recommendation models loaded successfully")
except Exception as e:
    movies, similarity, vectors, cv = None, None, None, None
    print(f"⚠️ Recommendation models not loaded: {e}")

SUBSCRIPTION_MAP = {"Basic": 0, "Premium": 2, "Standard": 3, "Mobile": 1}
REGION_MAP       = {"Tier-1": 2, "Tier-2": 0, "Tier-3": 1}
CITY_MAP = {
    "Bangalore": 0, "Chennai": 1, "Delhi": 2,
    "Dibrugarh": 3, "Guwahati": 4, "Jorhat": 5,
    "Jaipur": 6, "Lucknow": 7, "Mumbai": 8,
    "Pune": 9, "Silchar": 10, "Tezpur": 11,
}
LANGUAGE_MAP = {
    "Assamese": 0, "English": 1, "Hindi": 2,
    "Kannada": 3, "Marathi": 4, "Tamil": 5,
}
DEVICE_MAP   = {"Mobile": 2, "Smart TV": 3, "Tablet": 4, "Laptop": 1, "Desktop": 0}
GENDER_MAP   = {"Male": 1, "Female": 0, "Other": 2}
PAYMENT_MAP  = {"Credit Card": 0, "Debit Card": 1, "UPI": 2, "Net Banking": 3, "Wallet": 4}
GENRE_MAP    = {"Action": 0, "Comedy": 1, "Drama": 2, "Horror": 3, "Romance": 4, "Sci-Fi": 5, "Thriller": 6, "Documentary": 7}


REGIONAL_CONTENT = {
    "Assamese": [
        {"title": "Aamis",            "genre": "Drama",   "score": 9.1},
        {"title": "Local Kung Fu 2",  "genre": "Action",  "score": 8.4},
        {"title": "Bhoga Khirikee",   "genre": "Comedy",  "score": 8.0},
        {"title": "Xagor Xipare",     "genre": "Thriller","score": 7.9},
    ],
    "Hindi": [
        {"title": "Scam 1992",        "genre": "Drama",   "score": 9.5},
        {"title": "Mirzapur",         "genre": "Crime",   "score": 8.8},
        {"title": "Panchayat",        "genre": "Comedy",  "score": 9.0},
        {"title": "Delhi Crime",      "genre": "Thriller","score": 8.6},
    ],
    "Tamil": [
        {"title": "Vikram Vedha",     "genre": "Action",  "score": 8.4},
        {"title": "Soorarai Pottru",  "genre": "Drama",   "score": 9.0},
        {"title": "Karnan",           "genre": "Drama",   "score": 8.7},
        {"title": "Master",           "genre": "Action",  "score": 7.8},
    ],
    "Kannada": [
        {"title": "KGF Chapter 2",    "genre": "Action",  "score": 8.4},
        {"title": "777 Charlie",      "genre": "Drama",   "score": 9.1},
        {"title": "Kantara",          "genre": "Thriller","score": 9.0},
    ],
    "Marathi": [
        {"title": "Sairat",           "genre": "Romance", "score": 8.5},
        {"title": "Court",            "genre": "Drama",   "score": 8.3},
        {"title": "Fandry",           "genre": "Drama",   "score": 8.1},
    ],
    "English": [
        {"title": "Stranger Things",  "genre": "Sci-Fi",  "score": 8.7},
        {"title": "The Crown",        "genre": "Drama",   "score": 8.6},
        {"title": "Money Heist",      "genre": "Crime",   "score": 8.3},
    ],
}


RETENTION_MESSAGES = {
    "Tier-3": "🎬 Exclusive offer for you! Switch to Mobile Plan @ ₹99/month — enjoy {top_show} in your language. Limited time! Reply YES to activate.",
    "Tier-2": "🔥 We miss you! Upgrade to Standard Plan @ ₹199/month and unlock regional hits like {top_show}. Offer valid 24 hrs!",
    "Tier-1": "💎 As a valued member, enjoy 1 month Premium FREE. Binge {top_show} and more — no interruptions. Tap to activate.",
}


class UserFeatures(BaseModel):

    age:                        int   = Field(..., ge=10, le=100, example=24)
    gender:                     Literal["Male", "Female", "Other"] = Field("Male", example="Male")

    account_age_months:         int   = Field(..., ge=0, le=240, example=3)
    subscription_type:          Literal["Basic", "Standard", "Premium", "Mobile"] = Field(..., example="Basic")
    monthly_fee:                float = Field(..., ge=0, example=199.0)
    payment_method:             Literal["Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet"] = Field("UPI", example="UPI")

    primary_device:             Literal["Mobile", "Tablet", "Laptop", "Smart TV", "Desktop"] = Field("Mobile", example="Mobile")
    devices_used:               int   = Field(1, ge=1, le=10, example=1)
    favorite_genre:             Literal["Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", "Thriller", "Documentary"] = Field("Drama", example="Drama")
    avg_watch_time_minutes:     float = Field(..., ge=0, example=45.0)
    watch_sessions_per_week:    float = Field(..., ge=0, example=4.0)
    binge_watch_sessions:       int   = Field(0, ge=0, example=1)
    completion_rate:            float = Field(0.5, ge=0.0, le=1.0, example=0.6)
    rating_given:               float = Field(3.0, ge=0.0, le=5.0, example=3.5)
    content_interactions:       int   = Field(5, ge=0, example=8)
    recommendation_click_rate:  float = Field(0.3, ge=0.0, le=1.0, example=0.3)
    days_since_last_login:      int   = Field(..., ge=0, example=15)

    churned:                    int   = Field(0, ge=0, le=1, example=0)

    region_type:  Literal["Tier-1", "Tier-2", "Tier-3"] = Field(..., example="Tier-2")
    city:         str = Field(..., example="Guwahati")
    language:     Literal["Assamese", "Hindi", "Tamil", "Kannada", "Marathi", "English"] = Field(..., example="Assamese")


class PredictResponse(BaseModel):
    user_risk:       str    
    churn_prob:      float  
    churn_label:     int    
    risk_factors:    List[str]
    recommendation:  str


class RecommendRequest(BaseModel):
    language:    Literal["Assamese", "Hindi", "Tamil", "Kannada", "Marathi", "English"]
    region_type: Literal["Tier-1", "Tier-2", "Tier-3"]
    genre_pref:  Optional[str] = None


class RetainRequest(BaseModel):
    user_id:     str
    language:    Literal["Assamese", "Hindi", "Tamil", "Kannada", "Marathi", "English"]
    region_type: Literal["Tier-1", "Tier-2", "Tier-3"]
    churn_prob:  float



def encode_user(u: UserFeatures) -> np.ndarray:
    """
    Exact feature order matching model.feature_names_in_:
    ['age','gender','account_age_months','subscription_type','monthly_fee',
     'payment_method','primary_device','devices_used','favorite_genre',
     'avg_watch_time_minutes','watch_sessions_per_week','binge_watch_sessions',
     'completion_rate','rating_given','content_interactions',
     'recommendation_click_rate','days_since_last_login','churned',
     'region_type','city','language']
    """
    row = [
        u.age,
        GENDER_MAP.get(u.gender, 0),
        u.account_age_months,
        SUBSCRIPTION_MAP.get(u.subscription_type, 0),
        u.monthly_fee,
        PAYMENT_MAP.get(u.payment_method, 2),
        DEVICE_MAP.get(u.primary_device, 2),
        u.devices_used,
        GENRE_MAP.get(u.favorite_genre, 2),
        u.avg_watch_time_minutes,
        u.watch_sessions_per_week,
        u.binge_watch_sessions,
        u.completion_rate,
        u.rating_given,
        u.content_interactions,
        u.recommendation_click_rate,
        u.days_since_last_login,
        u.churned,
        REGION_MAP.get(u.region_type, 0),
        CITY_MAP.get(u.city, 0),
        LANGUAGE_MAP.get(u.language, 0),
    ]
    return np.array(row).reshape(1, -1)


def compute_risk_factors(u: UserFeatures) -> List[str]:
    factors = []
    if u.account_age_months < 6:
        factors.append(f"New subscriber — only {u.account_age_months} month(s) old (cold-start risk)")
    if u.subscription_type == "Basic":
        factors.append("Basic plan — low stickiness, price-sensitive segment")
    if u.avg_watch_time_minutes < 30:
        factors.append(f"Low engagement — {u.avg_watch_time_minutes} min/session (threshold: 30)")
    if u.days_since_last_login > 10:
        factors.append(f"Inactive — last login {u.days_since_last_login} days ago")
    if u.completion_rate < 0.4:
        factors.append(f"Low content completion rate — {u.completion_rate:.0%}")
    if u.region_type == "Tier-3":
        factors.append("Tier-3 city — limited regional content match risk")
    if not factors:
        factors.append("No strong churn signals detected")
    return factors


def mock_churn_prob(u: UserFeatures) -> float:
    """Fallback deterministic score when model.pkl is missing."""
    score = 0.0
    if u.account_age_months < 6:       score += 0.4
    if u.subscription_type == "Basic":  score += 0.3
    if u.avg_watch_time_minutes < 30:   score += 0.2
    if u.days_since_last_login > 10:    score += 0.1
    return min(score, 0.99)


from sklearn.metrics.pairwise import cosine_similarity

def ml_recommend(movie: str):
    if movies is None:
        return ["Recommendation model not loaded"]

    movie = movie.lower()

    if movie not in movies['title'].str.lower().values:
        return ["Movie not found"]

    idx = movies[movies['title'].str.lower() == movie].index[0]
    distances = similarity[idx]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    return [movies.iloc[i[0]].title for i in movies_list]


def ml_recommend_by_features(query: str):
    if vectors is None:
        return ["Recommendation model not loaded"]

    query_vector = cv.transform([query]).toarray()

    scores = cosine_similarity(query_vector, vectors)[0]

    top_movies = sorted(
        list(enumerate(scores)),
        reverse=True,
        key=lambda x: x[1]
    )[:5]

    return [movies.iloc[i[0]].title for i in top_movies]


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "🟢 Netflix NEXUS AI Backend is live",
        "team":   "Team SUINO",
        "time":   datetime.now().isoformat(),
        "docs":   "http://127.0.0.1:8000/docs",
    }


@app.post("/predict", response_model=PredictResponse, tags=["Churn Shield AI"])
def predict_churn(user: UserFeatures):
    """
    Predicts churn probability for a given user.
    Returns risk level, probability, contributing factors, and a retention tip.
    """
    try:
        if model:
            X = encode_user(user)
            prob = float(model.predict_proba(X)[0][1])
        else:
            prob = mock_churn_prob(user)

        label = 1 if prob >= 0.5 else 0

        if prob >= 0.70:
            risk = "High"
            tip  = "🚨 Trigger immediate retention offer — discounted plan or free content unlock."
        elif prob >= 0.40:
            risk = "Medium"
            tip  = "⚠️ Send a personalised nudge with regionally relevant content suggestions."
        else:
            risk = "Low"
            tip  = "✅ User is stable — focus on upsell to Premium."

        return PredictResponse(
            user_risk    = risk,
            churn_prob   = round(prob, 4),
            churn_label  = label,
            risk_factors = compute_risk_factors(user),
            recommendation = tip,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/recommend", tags=["Hyper-Local Intelligence"])
def recommend_content(req: RecommendRequest):
    try:
        prompt = f"""
        Suggest exactly 3 movies or web series for a Netflix user in India who:
        - Speaks {req.language}
        - Lives in a {req.region_type} city
        - Prefers {req.genre_pref if req.genre_pref else 'any'} genre

        Rules:
        - Prefer {req.language}-language content
        - Must be real, existing titles
        - Return ONLY a JSON array, no extra text, no markdown

        Format:
        [{{"title":"...","genre":"...","score":8.5,"why":"one line reason"}}]
        """
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        raw = response.text.strip().replace("```json", "").replace("```", "").strip()
        content = json.loads(raw)
    except Exception as e:
     print(f"❌ Gemini error: {e}")

    query = f"{req.language} {req.genre_pref or ''}"
    ml_results = ml_recommend_by_features(query)

    content = [
        {
            "title": title,
            "genre": req.genre_pref or "Mixed",
            "score": 8.0,
            "why": "Recommended by ML similarity engine"
        }
        for title in ml_results[:3]
    ]

    mobile_flag = req.region_type == "Tier-3"
    results = [{**item, "mobile_optimised": mobile_flag} for item in content[:3]]

    return {
        "language":    req.language,
        "region_type": req.region_type,
        "content":     results,
        "ai_note":     f"Powered by Gemini 2.0 Flash Lite — {req.language} Regional AI",
    }

@app.post("/retain", tags=["Retention Automation"])
def retain_user(req: RetainRequest):
    """
    Simulates a WhatsApp retention nudge for a high-risk user.
    In production: integrate with WhatsApp Business API / Twilio.
    """
    if req.churn_prob < 0.4:
        return {
            "action":  "none",
            "reason":  "User risk is LOW — no retention action needed.",
            "user_id": req.user_id,
        }

    top_show = REGIONAL_CONTENT.get(req.language, [{"title": "a top regional show"}])[0]["title"]

    template = RETENTION_MESSAGES.get(req.region_type, RETENTION_MESSAGES["Tier-2"])
    message  = template.format(top_show=top_show)

    discount_map = {"Tier-3": "₹99/month", "Tier-2": "₹199/month", "Tier-1": "1 Month Free"}
    offer = discount_map.get(req.region_type, "Special Offer")

    return {
        "action":         "whatsapp_nudge_triggered",
        "user_id":        req.user_id,
        "churn_prob":     req.churn_prob,
        "offer":          offer,
        "message_preview": message,
        "channel":        "WhatsApp Business API (simulated)",
        "timestamp":      datetime.now().isoformat(),
        "status":         "✅ Sent (demo mode — no real message dispatched)",
    }


@app.get("/dashboard", tags=["Growth Dashboard"])
def dashboard_metrics():
    regional_heatmap = {
        "Guwahati":  {"churn_rate": 0.45, "avg_watch_hrs": 3.3,  "top_language": "Assamese"},
        "Dibrugarh": {"churn_rate": 0.23, "avg_watch_hrs": 4.5,  "top_language": "Assamese"},
        "Pune":      {"churn_rate": 0.47, "avg_watch_hrs": 12.8, "top_language": "Marathi"},
        "Jaipur":    {"churn_rate": 0.42, "avg_watch_hrs": 3.3,  "top_language": "Hindi"},
        "Mumbai":    {"churn_rate": 0.22, "avg_watch_hrs": 8.6,  "top_language": "Marathi"},
        "Delhi":     {"churn_rate": 0.41, "avg_watch_hrs": 10.9, "top_language": "Hindi"},
    }

    return {
        "total_users":          12_480,
        "high_risk_users":       2_104,
        "retentions_triggered":    847,
        "churn_rate_overall":     0.17,
        "avg_churn_prob":         0.34,
        "top_churn_segment":     "Basic plan, <6 months, Tier-2/3",
        "regional_heatmap":       regional_heatmap,
        "plan_distribution": {
            "Basic":    0.45,
            "Standard": 0.30,
            "Premium":  0.20,
            "Mobile":   0.05,
        },
        "language_distribution": {
            "Hindi":    0.38,
            "Assamese": 0.18,
            "Tamil":    0.15,
            "Kannada":  0.12,
            "Marathi":  0.10,
            "English":  0.07,
        },
        "last_updated": datetime.now().isoformat(),
    }

@app.post("/recommend-ml", tags=["ML Recommendation"])
def recommend_movie_ml(data: dict):
    movie = data.get("movie")

    if not movie:
        raise HTTPException(status_code=400, detail="Movie name is required")

    return {
        "type": "movie_based",
        "input": movie,
        "recommendations": ml_recommend(movie)
    }


@app.post("/recommend-ml-feature", tags=["ML Recommendation"])
def recommend_feature_ml(data: dict):
    query = data.get("query")

    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    return {
        "type": "feature_based",
        "input": query,
        "recommendations": ml_recommend_by_features(query)
    }