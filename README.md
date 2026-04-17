# 🎬 Netflix NEXUS AI  
### 🚀 Hybrid AI Growth Engine for Churn Prediction, Regional Intelligence & Retention Automation

---

## 📌 Problem Statement & Objective

With increasing competition in OTT platforms, **user churn** has become a major challenge. Platforms like Netflix struggle to:

- Identify users likely to churn in advance  
- Personalize content for diverse regional audiences  
- Trigger timely retention strategies  

### 🎯 Objective
Build an **AI-powered system** that:
- Predicts user churn probability  
- Provides region-specific content recommendations  
- Automates retention actions for high-risk users  

---

## 🔍 Gap Analysis (Current vs Proposed Solution)

| Aspect | Current Systems | Proposed Solution (Netflix NEXUS AI) |
|--------|----------------|--------------------------------------|
| Churn Prediction | Reactive | ✅ Proactive AI-based prediction |
| Personalization | Generic recommendations | ✅ Region + language aware |
| Retention Strategy | Manual campaigns | ✅ Automated intelligent triggers |
| Regional Focus | Limited | ✅ Tier-based + hyper-local insights |
| Admin Control | Minimal | ✅ Interactive admin panel |

---

## 🏗️ System Architecture / Workflow

### 🔄 End-to-End Flow:

1. **User Input (Frontend - Streamlit)**  
   - Demographics, subscription, behavior data  

2. **Churn Prediction (FastAPI + ML Model)**  
   - RandomForest model predicts churn probability  

3. **Risk Analysis**  
   - Classifies user → Low / Medium / High risk  

4. **Recommendation Engine**  
   - Suggests region + language-based content  

5. **Retention Engine**  
   - Triggers personalized offers for high-risk users  

6. **Admin Panel**  
   - Monitor users, logs, insights, add content  

---

### 🧠 Architecture Diagram 
<img width="1536" height="1024" alt="ChatGPT Image Mar 24, 2026, 01_02_59 PM" src="https://github.com/user-attachments/assets/5efdbe6a-4393-4a59-aa6d-fda20219cd73" />




---

## ⚙️ Technology Stack

### 🖥️ Frontend
- Streamlit  
- Plotly (visualizations)  
- Custom CSS (Netflix-style UI)

### ⚙️ Backend
- FastAPI  
- Pydantic (data validation)  
- Uvicorn (server)

### 🤖 Machine Learning
- Scikit-learn (RandomForest)  
- Pandas, NumPy  
- Joblib / Pickle (model storage)

### 🧠 AI Integration
- Google Generative AI (Gemini) *(optional)*

---

## 🛠️ Setup & Execution Steps

### 1️⃣ Clone Repository
```bash
git clone <[https://github.com/Debashish-kashyap/SUINO_Hackathon_SemiFinal.git]>
cd netflix-nexus-ai
---

### 2️⃣ Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

### 3️⃣ Install Dependencies
pip install -r requirements.txt

### 4️⃣ Train Model Churn prediction
cd model
python train.py

### 5️⃣ Train model recommendation
cd backend
python train_recommender.py

### 6 Run Backend (FastAPI)
cd ../backend
uvicorn main:app --reload

### 7 Run Frontend (Streamlit)
cd ../dashboard
streamlit run app.py

---
```
## 🔮 Future Scope

- 🔗 Integration with real OTT APIs (Netflix, TMDB)  
- 📲 Real WhatsApp / Push Notification APIs  
- 📈 Real-time streaming data pipelines  
- 🧠 Deep Learning models (LSTM for behavior analysis)  
- 🌍 Multi-country localization  
- 📊 Explainable AI (SHAP integration)  

---

## ⚠️ Limitations

- Uses **synthetic dataset** (not real user data)  
- Retention system is **simulated (no real API integration)**  
- Model accuracy depends on generated patterns  
- Prototype-level scalability  

---

## 👨‍💻 Team
**Team SUINO**  
AI + Full Stack Innovation Project  



---
