# 🎬 Netflix Nexus AI

An AI-powered full-stack application that combines **Churn Prediction** and a **Movie Recommendation System** with an interactive dashboard.

---

## 🚀 Features

### 📊 1. Churn Prediction

* Predicts whether a user is likely to churn
* Built using Machine Learning model (`model.pkl`)
* FastAPI backend for real-time predictions

---

### 🎯 2. Movie Recommendation System

* Content-based recommendation engine

Suggests movies based

* Genre / feature input

---

### 🤖 3. Hybrid AI System

* Primary: LLM-based recommendations (if API available)
* Fallback: ML-based recommender (offline, no API needed)

---

### 📈 4. Streamlit Dashboard

* Interactive UI for:

  * Churn insights
  * Regional intelligence
  * Recommendations

---

## 🏗️ Project Structure

```
netflix-nexus-ai/
│
├── backend/
│   ├── main.py
│   ├── train_recommender.py
│   ├── movies.pkl
│   ├── similarity.pkl
│   ├── vectorizer.pkl
│   ├── vectors.pkl
│   └── model.pkl
│
├── dashboard/
│   └── app.py
│
├── data/
│   └── netflix_titles.csv / tmdb dataset
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/netflix-nexus-ai.git
cd netflix-nexus-ai
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Add Dataset

Place dataset inside `backend/`:

netflix_titles.csv

place dataset inside data/:

netflix_user_behavior_dataset.csv

---

### 5️⃣ Train Recommendation Model

```bash
cd backend
python train_recommender.py
```

✔️ This generates:

* movies.pkl
* similarity.pkl
* vectorizer.pkl
* vectors.pkl

---

### 6️⃣ Run Backend (FastAPI)
inside backend/

```bash
uvicorn main:app --reload
```

🔗 Open:

```
http://127.0.0.1:8000/docs
```

---

### 7️⃣ Run Dashboard (Streamlit)
inside venv

streamlit run dashboard/app.py


---

### *For working Prototype : Open Two terminal----In one: Run backend;    In another : Run Frontend (Streamlit)

## 🔌 API Endpoints

### 🔹 Churn Prediction

```
POST /predict
```

---

### 🔹 Movie Recommendation (ML)

```
POST /recommend-ml
```

---

### 🔹 Hybrid Recommendation

```
POST /recommend
```

---

## 🧠 Tech Stack

* **Backend:** FastAPI
* **Frontend:** Streamlit
* **ML:** Scikit-learn
* **Data:** Pandas, NumPy

---

## ⚠️ Notes

* If LLM API key is not available, system automatically switches to ML recommendations
* Ensure all `.pkl` files are inside `backend/`
* Run backend from inside `backend/` folder

---

## 💡 Future Improvements

* 🎬 Movie posters integration (TMDB API)
* ⭐ Ratings & reviews
* 👤 User-based collaborative filtering
* 🌐 Deployment (AWS / Render / Vercel)

---

## 👨‍💻 Author

Team SUINO

---

## ⭐ If you like this project, give it a star!
