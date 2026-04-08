import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv("custom_movies.csv", encoding='latin1')

movies['overview'] = movies['overview'].fillna('')
movies['genres'] = movies['genres'].fillna('')
movies['language'] = movies['language'].fillna('')

movies['tags'] = movies['overview'] + " " + movies['genres'] + " " + movies['language']

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(movies['tags']).toarray()

similarity = cosine_similarity(vectors)

pickle.dump(movies, open("movies.pkl", "wb"))
pickle.dump(similarity, open("similarity.pkl", "wb"))
pickle.dump(cv, open("vectorizer.pkl", "wb"))
pickle.dump(vectors, open("vectors.pkl", "wb"))

print("✅ Language-aware model created!")