import pandas as pd
import numpy as np
import random

df = pd.read_csv("data/netflix_user_behavior_dataset.csv")

df.columns = df.columns.str.lower().str.replace(" ", "_")


df['country'] = 'India'


df['region_type'] = random.choices(
    ['Tier-1', 'Tier-2', 'Tier-3'],
    weights=[0.3, 0.4, 0.3],
    k=len(df)
)

tier_1_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai']
tier_2_cities = ['Guwahati', 'Pune', 'Jaipur', 'Lucknow']
tier_3_cities = ['Dibrugarh', 'Silchar', 'Tezpur', 'Jorhat']

def assign_city(tier):
    if tier == 'Tier-1':
        return random.choice(tier_1_cities)
    elif tier == 'Tier-2':
        return random.choice(tier_2_cities)
    else:
        return random.choice(tier_3_cities)

df['city'] = df['region_type'].apply(assign_city)


def assign_language(city):
    if city in ['Guwahati', 'Dibrugarh', 'Silchar', 'Tezpur', 'Jorhat']:
        return 'Assamese'
    elif city in ['Mumbai', 'Pune']:
        return random.choice(['Hindi', 'Marathi'])
    elif city == 'Chennai':
        return 'Tamil'
    elif city == 'Bangalore':
        return random.choice(['Kannada', 'English'])
    else:
        return random.choice(['Hindi', 'English'])

df['language'] = df['city'].apply(assign_language)



df['churn'] = (
    (df['account_age_months'] < 6) & 
    (df['subscription_type'] == 'Basic')
).astype(int)


for col in df.select_dtypes(include=['object', 'category']).columns:
    if col not in ['user_id']:  
        df[col] = df[col].astype('category').cat.codes



features = [col for col in df.columns if col not in ['churn', 'user_id', 'country']]

X = df[features]
y = df['churn']



from sklearn.ensemble import RandomForestClassifier
import pickle

model = RandomForestClassifier()
model.fit(X, y)

pickle.dump(model, open("model.pkl", "wb"))


print("✅ Model trained successfully!")
print(df[['country', 'region_type', 'city', 'language']].head())