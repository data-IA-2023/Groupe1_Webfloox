from sqlalchemy import create_engine
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Database URL
db_url = "postgresql://citus:floox2024!@c-groupe4.tlvz7y727exthe.postgres.cosmos.azure.com:5432/netfloox"

# Create engine
engine = create_engine(db_url)

# Define the SQL query to fetch data from the view
sql_query_rec = """SELECT * FROM netfloox_complet.recommendation"""

# Read the data into a pandas DataFrame
df = pd.read_sql(sql_query_rec, engine)

# Close the database connection
engine.dispose()

df['primaryTitle'].fillna('', inplace=True)
df['genres'] = df['genres'].fillna('')
df['genres'] =  df['genres'].str.replace(',', ' ')
df['actors'] = df['actors'].astype(str) 
df['directors'] =df['directors'].astype(str)
df['genres'] = df['genres'].fillna('')
df['averageRating'] =df['averageRating'].astype(str)

# For simplicity,  fill missing values for categorical data with a placeholder and numerical with median
df.fillna({'primaryTitle': 'Unknown', 'directors': 'Unknown', 'actors': 'Unknown', 
           'genres': 'Unknown'}, inplace=True)

df.dropna()

# Combine textual features
df['startYear'] = df['startYear'].astype(str)
df['numVotes'] = df['numVotes'].astype(str)
df['combined_features'] = df['primaryTitle']+ ' ' + df['directors'] + ' ' + df['actors']  + ' ' + df['startYear'] + ' ' + df['numVotes'] + ' ' + df['averageRating']
# TF-IDF Vectorization for the combined textual features
vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
combined_features_tfidf = vectorizer.fit_transform(df['combined_features'])

# Create a mapping from film titles to their indices in the feature matrix
film_to_index = pd.Series(df.index, index=df['primaryTitle']).to_dict()


def get_recommendations(films, num_recom=17): #Ca donne que 15 recommendations
    # Check if the film exists in our mapping
    recom = []
    for film_name in films:
        if film_name in film_to_index:
            # Get the index of the film from its name
            idx = film_to_index[film_name]
            # Compute cosine similarity between the film's features and the features of all films
            cosine_sim = cosine_similarity(combined_features_tfidf, combined_features_tfidf[idx].reshape(1, -1))
            
            # Get pairwise similarity scores for all films with that film
            sim_scores = list(enumerate(cosine_sim.flatten()))
            
            # Sort the films based on the similarity scores
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Get the scores of the 50 most similar films, skip the first one since it is the query film itself
            sim_scores = sim_scores[1:51]
            
            # Get the film indices
            film_indices = [i[0] for i in sim_scores]
            
            # Return the top 50 most similar films
            recom.append(df.iloc[film_indices]['primaryTitle'].to_list())
    results = []
    l=len(recom)
    j=0
    for i in range(num_recom):
        if i>=l :
            results.append(recom[i%l][j])
            j+=1
    return results