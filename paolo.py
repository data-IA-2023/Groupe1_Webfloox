#First we get our recommendation model

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler, FunctionTransformer, LabelEncoder, OneHotEncoder
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import create_engine
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.base import BaseEstimator, TransformerMixin
from scipy import sparse 

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

df['title'].fillna('', inplace=True)
df['genres'] = df['genres'].fillna('')
df['genres'] =  df['genres'].str.replace(',', ' ')
df['actor'] = df['actor'].astype(str) 
df['director'] =df['director'].astype(str)
df['writer'] =df['writer'].astype(str)
df['genres'] = df['genres'].fillna('')
df['averageRating'] =df['averageRating'].astype(str)

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
# For simplicity,  fill missing values for categorical data with a placeholder and numerical with median
df.fillna({'title': 'Unknown', 'director': 'Unknown', 'actor': 'Unknown', 
           'genres': 'Unknown', 'writer': 'Unknown'}, inplace=True)

# Imputing missing numerical values with median
num_imputer = SimpleImputer(strategy='median')
df[['startYear', 'runtimeMinutes']] = num_imputer.fit_transform(df[['startYear', 'runtimeMinutes']])

# Normalize 'startYear' and 'runtimeMinutes'
scaler = MinMaxScaler()
df[['startYear', 'runtimeMinutes']] = scaler.fit_transform(df[['startYear', 'runtimeMinutes']])

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Combine textual features
df['combined_features'] = df['title']+ ' ' + df['title']+ ' ' + df['director'] + ' ' + df['actor'] + ' ' + df['genres'] + ' ' + df['writer']

# TF-IDF Vectorization for the combined textual features
vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
combined_features_tfidf = vectorizer.fit_transform(df['combined_features'])

