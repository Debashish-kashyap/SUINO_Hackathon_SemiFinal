import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv("netflix_titles.csv", encoding='latin1')

movies['description'] = movies['description'].fillna('')
movies['listed_in'] = movies['listed_in'].fillna('')

movies['tags'] = movies['description'] + " " + movies['listed_in']

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(movies['tags']).toarray()

similarity = cosine_similarity(vectors)

pickle.dump(movies, open("movies.pkl", "wb"))
pickle.dump(similarity, open("similarity.pkl", "wb"))
pickle.dump(cv, open("vectorizer.pkl", "wb"))
pickle.dump(vectors, open("vectors.pkl", "wb"))

print("✅ Netflix dataset model created!")