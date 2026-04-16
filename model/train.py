import pandas as pd
import numpy as np
import random
import os
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


df = pd.read_csv("../data/netflix_user_behavior_dataset.csv")


df.columns = df.columns.str.lower().str.replace(" ", "_")


fee_map = {
    7.99: 199,
    12.99: 499,
    15.99: 649
}

df['monthly_fee'] = df['monthly_fee'].round(2).map(fee_map)
df['monthly_fee'] = df['monthly_fee'].fillna(199)


df['country'] = 'India'

df['region_type'] = random.choices(
    ['Tier-1', 'Tier-2', 'Tier-3'],
    weights=[0.3, 0.4, 0.3],
    k=len(df)
)

tier_1 = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai']
tier_2 = ['Guwahati', 'Pune', 'Jaipur', 'Lucknow']
tier_3 = ['Dibrugarh', 'Silchar', 'Tezpur', 'Jorhat']

def assign_city(t):
    return random.choice(tier_1 if t=='Tier-1' else tier_2 if t=='Tier-2' else tier_3)

df['city'] = df['region_type'].apply(assign_city)

def assign_language(c):
    if c in tier_3: return 'Assamese'
    if c in ['Mumbai','Pune']: return random.choice(['Hindi','Marathi'])
    if c=='Chennai': return 'Tamil'
    if c=='Bangalore': return random.choice(['Kannada','English'])
    return random.choice(['Hindi','English'])

df['language'] = df['city'].apply(assign_language)


np.random.seed(42)

churn_prob = (
    0.25 * (df['account_age_months'] < 6).astype(int) +
    0.20 * (df['subscription_type'] == 'Basic').astype(int) +
    0.20 * (df['avg_watch_time_minutes'] < 30).astype(int) +
    0.15 * (df['days_since_last_login'] > 10).astype(int) +
    0.10 * (df['completion_rate'] < 0.4).astype(int) +
    np.random.normal(0, 0.1, len(df))  
)

churn_prob = np.clip(churn_prob, 0, 1)

df['churned'] = (churn_prob > 0.5).astype(int)


for col in df.select_dtypes(include=['object', 'string']).columns:
    if col not in ['user_id']:
        df[col] = df[col].astype('category').cat.codes


features = [col for col in df.columns if col not in ['churned', 'user_id', 'country']]

X = df[features]
y = df['churned']


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=8,
    min_samples_split=5,
    random_state=42
)

model.fit(X_train, y_train)


y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("✅ Model trained successfully!")
print(f"🎯 Accuracy: {accuracy:.2f}")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, "backend", "model.pkl")
features_path = os.path.join(BASE_DIR, "backend", "features.pkl")

with open(model_path, "wb") as f:
    pickle.dump(model, f)

with open(features_path, "wb") as f:
    pickle.dump(features, f)

print(f"💾 Model saved at: {model_path}")
print(f"💾 Features saved at: {features_path}")

print("\n💰 Fee values:", df['monthly_fee'].unique())
print("❗ Missing:", df['monthly_fee'].isna().sum())