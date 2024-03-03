from imports2 import *

with open('.env', 'r') as json_file:
    env = json.load(json_file)
    username=env["username"]
    password=env["password"]
    hostname=env["hostname"]
    port=env["port"]
    db=env["db"]
 
conn_string = f"host={hostname} dbname={db} user={username} password={password}  "
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()



def db_to_vectorized(cursor):
    cursor.execute(''' select tb.tconst, tb."primaryTitle", tb."titleType", tb.genres, 
    tb."startYear", tb."runtimeMinutes", 
    array_to_string(cbt."actor",','),
    array_to_string(cbt."director",','),
    array_to_string(cbt."writer",','),
    tr."averageRating", tr."numVotes",
    count(ta.title) As "countTitleByRegion"
    from "titleBasics" tb 
    full outer join "titleAkas" ta 
    on tb.tconst = ta."titleId" 
    full outer join cast_by_title cbt 
    on tb.tconst = cbt.tconst 
    full outer join "titleRatings" tr 
    on tb.tconst  = tr.tconst 
    where
    tb."isAdult" = 0  AND tb."titleType" LIKE 'movie'
    group by tb.tconst,
    cbt."actor",cbt."director",cbt."writer",
    tr."averageRating", tr."numVotes"
    ORDER BY tr."numVotes" DESC NULLS LAST, tr."averageRating" DESC NULLS LAST
    LIMIT 500000 ''')

    movie = cursor.fetchall()
    df = pd.DataFrame(movie , columns=["tconst","title","titleType","genres","startYear","runtimeMinutes","actor","director","writer","averageRating","numVotes","countTitleByRegion" ])

    # knn model 
    # 



    df['title'] = df['title'].fillna('', inplace=True)
    df['genres'] = df['genres'].fillna('')
    df['genres'] =  df['genres'].str.replace(',', ' ')
    df['actor'] = df['actor'].astype(str) 
    df['director'] =df['director'].astype(str)
    df['writer'] =df['writer'].astype(str)
    df['genres'] = df['genres'].fillna('')
    df['averageRating'] =df['averageRating'].astype(str)


    # For simplicity,  fill missing values for categorical data with a placeholder and numerical with median
    df.fillna({'title': 'Unknown', 'director': 'Unknown', 'actor': 'Unknown', 
            'genres': 'Unknown', 'writer': 'Unknown'}, inplace=True)

    # Imputing missing numerical values with median
    num_imputer = SimpleImputer(strategy='median')
    df[['startYear', 'runtimeMinutes']] = num_imputer.fit_transform(df[['startYear', 'runtimeMinutes']])

    # Normalize 'startYear' and 'runtimeMinutes'
    scaler = MinMaxScaler()
    df[['startYear', 'runtimeMinutes']] = scaler.fit_transform(df[['startYear', 'runtimeMinutes']])




    # Combine textual features
    df['combined_features'] = df['title']+ ' ' + df['title']+ ' ' + df['director'] + ' ' + df['actor'] + ' ' + df['genres'] + ' ' + df['writer']

    # TF-IDF Vectorization for the combined textual features
    vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
    combined_features_tfidf = vectorizer.fit_transform(df['combined_features'])
    return combined_features_tfidf,df




def suggest_movie_name_contains(input_movie_name, df):
    # Normalize the input movie name to lowercase for case-insensitive matching
    input_movie_name_lower = input_movie_name.lower()
    
    # Filter the DataFrame for titles that contain the input string
    contains_match_df = df[df['title'].str.lower().str.contains(input_movie_name_lower)]
    
    # If one or more matches are found, return the title of the first match
    if not contains_match_df.empty:
        return contains_match_df.iloc[0]['title']  # Return the first matching title
    else:
        return None
    


def get_recommendations(movie_name, df, model_knn, vectorizer):
    # Transform movie_name to match the features space
    movie_features = vectorizer.transform([movie_name])
    
    # Find similar movies
    distances, indices = model_knn.kneighbors(movie_features, n_neighbors=50)
    
    recommendations = []
    
    for i in range(0, len(distances.flatten())):

        if i == 0:
            print(f'Recommendations for "{movie_name}":\n')
        else:
            # Append recommendation details to the list
            index = indices.flatten()[i]  # Get the original DataFrame index for the recommended item
            recommendations.append({
                'index': df.index[index],
                'title': df.iloc[indices.flatten()[i]]['title'],
                'Distance': distances.flatten()[i],
                'rating': df['averageRating'][i] 
            })
           
            
    
    # Convert the list of recommendations to a DataFrame
 
    recommendations_df = pd.DataFrame(recommendations)
    return recommendations_df 


# Function to get cosine similarity for a given movie name
def get_cosine_similarity(movie_name, count_matrix, movie_to_index):
    # Get the index of the movie from the name
    idx = movie_to_index.get(movie_name)
    if idx is not None:
        # Compute cosine similarity between the movie vector and all vectors
        cosine_sim = cosine_similarity(count_matrix, count_matrix[idx].reshape(1, -1))
        return cosine_sim
    else:
        return None



# Create a mapping from movie titles to their indices in the feature matrix


def get_cosine_sim_recommendations(movie_name, df, combined_features_tfidf, movie_to_index):
    # Check if the movie exists in our mapping
    if movie_name in movie_to_index:
        # Get the index of the movie from its name
        idx = movie_to_index[movie_name]
        # Compute cosine similarity between the movie's features and the features of all movies
        cosine_sim = cosine_similarity(combined_features_tfidf, combined_features_tfidf[idx].reshape(1, -1))
        
        # Get pairwise similarity scores for all movies with that movie
        sim_scores = list(enumerate(cosine_sim.flatten()))
        
        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get the scores of the 50 most similar movies, skip the first one since it is the query movie itself
        sim_scores = sim_scores[1:51]
        
        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]
        
        # Return the top 50 most similar movies
        return  df.iloc[movie_indices][['title']].reset_index()
    else:
        return None


def find_all_close_titles(tit, df):
    # Lowercase the title for case-insensitive matching
    tit = tit.lower()
    # Ensure the title column is in lowercase for matching
    temp_df = df.copy()
    temp_df['title'] = temp_df['title'].str.lower()
    # Find titles that exactly match or closely match the partial title
    close_matches = temp_df[temp_df['title'].str.contains(tit)]
    return close_matches

def rec_mov(partial_movie_title, df, cosine_sim):
    partial_movie_title = partial_movie_title.lower()
    close_matches_df = find_all_close_titles(partial_movie_title, df)
    
    if close_matches_df.empty:
        return pd.DataFrame()  # Return an empty DataFrame if no matches
    
    # Assuming there could be multiple close matches, we'll use the first one for simplicity
    first_match_index = close_matches_df.index[0]
    sim_scores = list(enumerate(cosine_sim[first_match_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]  # Get top 5 matches, excluding the movie itself
    
    movie_indices = [i[0] for i in sim_scores]
    recommended_movies = df.iloc[movie_indices]
    
    return recommended_movies[['title', 'actor']]  # Adjust columns to those actually available


# # Building the recommendation model
# model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
# model_knn.fit(combined_features_tfidf)

# movie_name1 = input("Enter the name of the movie: ")
# movie_name = suggest_movie_name_contains(movie_name1, df)
# rec_knn = get_recommendations(movie_name, df, model_knn, vectorizer)
# print(rec_knn)


# dfc=df
# dfc['startYear'] = dfc['startYear'].astype(str)
# dfc['runtimeMinutes'] = dfc['runtimeMinutes'].astype(str)
# dfc['combined_features'] = dfc['title']+ ' ' + dfc['title'] + ' ' + dfc['director'] + ' ' + dfc['actor'] + ' ' + dfc['genres'] + ' ' + dfc['writer'] + ' ' + dfc['startYear'] + ' ' + dfc['runtimeMinutes']
# couv = CountVectorizer(stop_words='english', max_features= 500)
# count_matrix = couv.fit_transform(dfc['combined_features'])
# print(count_matrix)

# movie_to_index = pd.Series(df.index, index=df['title']).to_dict()


# cosine_sim = get_cosine_similarity(movie_name, count_matrix, movie_to_index)

# recommendations = get_cosine_sim_recommendations(movie_name, df, combined_features_tfidf, movie_to_index)
# # Assuming you have a user input mechanism in place
# user_input_movie = input("Enter the movie's name: ")
# recommended_movies = rec_mov(user_input_movie, df, cosine_sim).head(5)
# content_cosine = pd.DataFrame(recommendations).astype(str)
# rec_knn=rec_knn.astype(str)
# matched_df = pd.merge(content_cosine, rec_knn, on=('index', 'title'), how='inner')
# matched_df.head(5)


# couv = CountVectorizer(stop_words='english', max_features= 5000)
# count_matrix = couv.fit_transform(dfc['combined_features'])
# cosine_sim = cosine_similarity(count_matrix)