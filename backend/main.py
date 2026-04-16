from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import pickle
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime
from google import genai
import json

BASE_DIR = os.path.dirname(__file__)

# client = genai.Client(api_key="API KEY")
# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents="Hello"
# )
# 
# print(response.text)

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
    model_path = os.path.join(BASE_DIR, "model.pkl")

    model = joblib.load(model_path)
    print("✅ model.pkl loaded successfully")
except FileNotFoundError:
    model = None
    print("⚠️  model.pkl not found — /predict will return mock scores")


try:
    movies = pickle.load(open(os.path.join(BASE_DIR, "movies.pkl"), "rb"))
    similarity = pickle.load(open(os.path.join(BASE_DIR, "similarity.pkl"), "rb"))
    vectors = pickle.load(open(os.path.join(BASE_DIR, "vectors.pkl"), "rb"))
    cv = pickle.load(open(os.path.join(BASE_DIR, "vectorizer.pkl"), "rb"))
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

RETENTION_LOGS = []

MOCK_USERS = [
    {"user_id": "USR_MUM_24", "age": 24, "region_type": "Tier-1", "language": "Marathi", "churn_prob": 0.12, "risk_level": "Low"},
    {"user_id": "USR_DIB_19", "age": 19, "region_type": "Tier-3", "language": "Assamese", "churn_prob": 0.88, "risk_level": "High"},
    {"user_id": "USR_PUN_35", "age": 35, "region_type": "Tier-2", "language": "Hindi", "churn_prob": 0.45, "risk_level": "Medium"},
    {"user_id": "USR_CHE_42", "age": 42, "region_type": "Tier-1", "language": "Tamil", "churn_prob": 0.18, "risk_level": "Low"},
    {"user_id": "USR_GUW_28", "age": 28, "region_type": "Tier-2", "language": "Assamese", "churn_prob": 0.65, "risk_level": "High"},
]

class AddMovieRequest(BaseModel):
    title: str
    genre: Optional[str] = None
    genres: Optional[str] = None
    language: str


class UserFeatures(BaseModel):

    age:                    int   = Field(..., ge=10, le=100, example=24)
    account_age_months:     int   = Field(..., ge=0, le=240, example=3)
    subscription_type:      Literal["Basic", "Standard", "Premium", "Mobile"] = Field(..., example="Basic")
    monthly_fee:            float = Field(..., ge=0, example=199.0)
    avg_watch_time_minutes: float = Field(..., ge=0, example=45.0)
    watch_sessions_per_week: float = Field(..., ge=0, example=4.0)
    completion_rate:        float = Field(..., ge=0.0, le=1.0, example=0.5)
    days_since_last_login:  int   = Field(..., ge=0, example=15)
    region_type:            Literal["Tier-1", "Tier-2", "Tier-3"] = Field(..., example="Tier-2")
    language:               Literal["Assamese", "Hindi", "Tamil", "Kannada", "Marathi", "English"] = Field(..., example="Assamese")

    gender:                    Optional[Literal["Male", "Female", "Other"]] = Field(None)
    payment_method:            Optional[Literal["Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet"]] = Field(None)
    primary_device:            Optional[Literal["Mobile", "Tablet", "Laptop", "Smart TV", "Desktop"]] = Field(None)
    devices_used:              Optional[int]   = Field(None)
    favorite_genre:            Optional[Literal["Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", "Thriller", "Documentary"]] = Field(None)
    binge_watch_sessions:      Optional[int]   = Field(None)
    rating_given:              Optional[float] = Field(None)
    content_interactions:      Optional[int]   = Field(None)
    recommendation_click_rate: Optional[float] = Field(None)
    churned:                   Optional[int]   = Field(None)
    city:                      Optional[str]   = Field(None)


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



FIELD_AVERAGES = {
    "gender":                    1,      
    "payment_method":            2,      
    "primary_device":            2,     
    "devices_used":              2,
    "favorite_genre":            2,      
    "binge_watch_sessions":      2,
    "rating_given":              3.5,
    "content_interactions":      15,
    "recommendation_click_rate": 0.35,
    "churned":                   0,
    "city":                      4,      
}


def encode_user(u: UserFeatures) -> np.ndarray:
    """
    Exact feature order matching model.feature_names_in_:
    ['age','gender','account_age_months','subscription_type','monthly_fee',
     'payment_method','primary_device','devices_used','favorite_genre',
     'avg_watch_time_minutes','watch_sessions_per_week','binge_watch_sessions',
     'completion_rate','rating_given','content_interactions',
     'recommendation_click_rate','days_since_last_login','churned',
     'region_type','city','language']
    Optional fields use dataset averages when None.
    """
    row = [
        u.age,
        GENDER_MAP.get(u.gender, FIELD_AVERAGES["gender"]) if u.gender else FIELD_AVERAGES["gender"],
        u.account_age_months,
        SUBSCRIPTION_MAP.get(u.subscription_type, 0),
        u.monthly_fee,
        PAYMENT_MAP.get(u.payment_method, FIELD_AVERAGES["payment_method"]) if u.payment_method else FIELD_AVERAGES["payment_method"],
        DEVICE_MAP.get(u.primary_device, FIELD_AVERAGES["primary_device"]) if u.primary_device else FIELD_AVERAGES["primary_device"],
        u.devices_used if u.devices_used is not None else FIELD_AVERAGES["devices_used"],
        GENRE_MAP.get(u.favorite_genre, FIELD_AVERAGES["favorite_genre"]) if u.favorite_genre else FIELD_AVERAGES["favorite_genre"],
        u.avg_watch_time_minutes,
        u.watch_sessions_per_week,
        u.binge_watch_sessions if u.binge_watch_sessions is not None else FIELD_AVERAGES["binge_watch_sessions"],
        u.completion_rate,
        u.rating_given if u.rating_given is not None else FIELD_AVERAGES["rating_given"],
        u.content_interactions if u.content_interactions is not None else FIELD_AVERAGES["content_interactions"],
        u.recommendation_click_rate if u.recommendation_click_rate is not None else FIELD_AVERAGES["recommendation_click_rate"],
        u.days_since_last_login,
        REGION_MAP.get(u.region_type, 0),
        CITY_MAP.get(u.city, FIELD_AVERAGES["city"]) if u.city else FIELD_AVERAGES["city"],
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
    if u.account_age_months < 6:        score += 0.4
    if u.subscription_type == "Basic":  score += 0.3
    if u.avg_watch_time_minutes < 30:   score += 0.2
    if u.days_since_last_login > 10:    score += 0.1
    return min(score, 0.99)




from sklearn.metrics.pairwise import cosine_similarity

def ml_recommend(movie: str):
    if movies is None:
        return [item["title"] for item in REGIONAL_CONTENT.get("Hindi", [])[:3]]

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
    if vectors is None or movies is None:
    
        for lang in REGIONAL_CONTENT:
            if lang.lower() in query.lower():
                return [item["title"] for item in REGIONAL_CONTENT[lang][:3]]
        default = next(iter(REGIONAL_CONTENT.values()))
        return [item["title"] for item in default[:3]]

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
        if movies is None or similarity is None:
            raise Exception("ML models not loaded")

        import random

        filtered = movies[movies['language'].str.lower() == req.language.lower()]

        if req.genre_pref:
            filtered = filtered[
                filtered['genres'].str.contains(req.genre_pref, case=False, na=False)
            ]

        if len(filtered) < 10:
            filtered = movies

        random_idx = random.choice(filtered.index.tolist())

        distances = similarity[random_idx]

        movies_list = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )

        results = []

        for i in movies_list:
            row = movies.iloc[i[0]]

            if row['language'].lower() != req.language.lower():
                continue

            if req.genre_pref:
                if req.genre_pref.lower() not in row["genres"].lower():
                    continue

            results.append({
                "title": row["title"],
                "genre": row["genres"],
                "score": round(float(i[1]), 2),
                "why": f"Similar to {movies.iloc[random_idx]['title']}",
                "mobile_optimised": req.region_type == "Tier-3"
            })

            if len(results) == 5:
                break


        return {
            "language": req.language,
            "region_type": req.region_type,
            "content": results,
            "ai_note": "Powered by ML similarity engine (language + genre aware)"
        }

    except Exception as e:
       return {"error": str(e)}

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
    
    timestamp = datetime.now().isoformat()
    
    RETENTION_LOGS.append({
        "user_id": req.user_id,
        "offer": offer,
        "timestamp": timestamp
    })

    return {
        "action":         "whatsapp_nudge_triggered",
        "user_id":        req.user_id,
        "churn_prob":     req.churn_prob,
        "offer":          offer,
        "message_preview": message,
        "channel":        "WhatsApp Business API (simulated)",
        "timestamp":      timestamp,
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


@app.get("/admin/users", tags=["Admin"])
def get_admin_users():
    return {"users": MOCK_USERS}

@app.get("/admin/retention-logs", tags=["Admin"])
def get_retention_logs():
    return {"logs": RETENTION_LOGS}

@app.post("/admin/add-movie", tags=["Admin"])
def admin_add_movie(req: AddMovieRequest):
    global movies  
    
    genre_val = req.genre if req.genre else req.genres
    if not genre_val:
        genre_val = "Unknown"
        
    if req.language in REGIONAL_CONTENT:
        REGIONAL_CONTENT[req.language].append({"title": req.title, "genre": genre_val, "score": 8.0})
    else:
        REGIONAL_CONTENT[req.language] = [{"title": req.title, "genre": genre_val, "score": 8.0}]
        
    if movies is not None:
        try:
            new_row = pd.DataFrame([{"title": req.title, "genres": genre_val, "language": req.language}])
            movies = pd.concat([movies, new_row], ignore_index=True)
        except Exception as e:
            print("Could not append to movies DataFrame:", e)
            
    return {"status": "success", "message": f"Successfully added '{req.title}'."}

@app.get("/admin/insights", tags=["Admin"])
def get_admin_insights():
    if not MOCK_USERS:
        return {"error": "No users available for insights."}
        
    avg_churn = sum(u["churn_prob"] for u in MOCK_USERS) / len(MOCK_USERS)
    
    langs = [u["language"] for u in MOCK_USERS]
    most_common_lang = max(set(langs), key=langs.count)
    
    region_churn = {}
    region_counts = {}
    for u in MOCK_USERS:
        reg = u["region_type"]
        region_churn[reg] = region_churn.get(reg, 0) + u["churn_prob"]
        region_counts[reg] = region_counts.get(reg, 0) + 1
        
    avg_region_churn = {r: region_churn[r] / region_counts[r] for r in region_churn}
    top_churn_region = max(avg_region_churn, key=avg_region_churn.get)
    
    return {
        "top_churn_region": top_churn_region,
        "most_common_language": most_common_lang,
        "avg_churn_probability": round(avg_churn, 4)
    }