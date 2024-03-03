from imports2 import *

def create_conn(hostname,db,username,password,port):
    conn_string = f"host={hostname} port={port} dbname={db} user={username} password={password}"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor,conn



def fetch_user_favs(cursor):
    cursor.execute("""
    SELECT "user", title
    FROM netfloox_complet.user_liked_movies;
    """)
    result=cursor.fetchall()
    result2=[]
    for i in range(len(result)) :
        result2.append([])
        for j in range(len(result[i])):
            if type(result[i][j])==str : result2[i].append(result[i][j].replace("_singlequote_","'"))
            else : result2[i].append(result[i][j])
    return result2

def fetch_users(cursor):
    cursor.execute("""
    SELECT "user","password","light_mode"
    FROM netfloox_complet.user;
    """)
    result=cursor.fetchall()
    result2=[]
    for i in range(len(result)) :
        result2.append([])
        for j in range(len(result[i])):
            if type(result[i][j])==str : result2[i].append(result[i][j].replace("_singlequote_","'"))
            else : result2[i].append(result[i][j])
    return result2

def fetch_history(cursor):
    cursor.execute("""
    SELECT "user", "movies_seen"
    FROM netfloox_complet.user_history;
    """)
    result=cursor.fetchall()
    result2=[]
    for i in range(len(result)) :
        result2.append([])
        for j in range(len(result[i])):
            if type(result[i][j])==str : result2[i].append(result[i][j].replace("_singlequote_","'"))
            else : result2[i].append(result[i][j])
    return result2

def super_function(cursor):

    

    result = fetch_user_favs(cursor)

    d={}

    for e in result:
        d[e[0]]=[]
    for e in result:
        if d[e[0]] != None : d[e[0]]=d[e[0]] + [e[1]]

    

    result = fetch_users(cursor)

    d2={}
    for e in result:
        d2[e[0]]=e[1]

    d3={}
    for e in result:
        d3[e[0]]=e[2]


    

    result = fetch_history(cursor)

    d4={}
    for e in result:
        d4[e[0]]=[]

    for e in result:
        if d4[e[0]] != None : d4[e[0]]=d4[e[0]] + [e[1]]
    return d2,d,d3,d4

def create_user(cursor,user,hashed_pwd):
    cursor.execute(f"""
    INSERT INTO netfloox_complet.user ("user","password","light_mode")
    VALUES ('{user.replace("'","_singlequote_")}','{hashed_pwd.replace("'","_singlequote_")}',FALSE);
    """)


def write_history(cursor,user,movie):
    cursor.execute(f"""
    INSERT INTO netfloox_complet.user_history ("user","movies_seen")
    VALUES ('{user.replace("'","_singlequote_")}','{movie.replace("'","_singlequote_")}');
    """)

def write_favourite(cursor,user,movie,isliked):
    if isliked : 
        cursor.execute(f"""
        DELETE FROM netfloox_complet.user_liked_movies
        WHERE "user" = '{user.replace("'","_singlequote_")}' AND "title" = '{movie.replace("'","_singlequote_")}';
        """)
    else :
        cursor.execute(f"""
        INSERT INTO netfloox_complet.user_liked_movies ("user","title")
        VALUES ('{user.replace("'","_singlequote_")}','{movie.replace("'","_singlequote_")}');
        """)


def change_lightmode(cursor,user,lightmode):
    cursor.execute(f"""
    UPDATE netfloox_complet.user
    SET "light_mode" = {"TRUE" if lightmode == True else "FALSE"}
    WHERE "user" = '{user.replace("'","_singlequote_")}';
    """)

# Recommendation part

def create_df(cursor):
    cursor.execute("""SELECT * FROM netfloox_complet.recommendation""")
    results=cursor.fetchall()
    df = pd.DataFrame(results,columns=["averageRating","numVotes","primaryTitle","startYear","genres","actors","directors"])
    return df



def get_cosine_sim_recommendations(df, movies, num_recom):
    """
    df['averageRating'] = df['averageRating'].astype(str)
    df['startYear'] = df['startYear'].astype(str)
    df['numVotes'] = df['numVotes'].astype(str)
    df['combined_features'] = df['primaryTitle']+ ' ' + df['directors'] + ' ' + df['actors']  + ' ' + df['startYear'] + ' ' + df['numVotes'] + ' ' + df['averageRating']"""
    df['combined_features'] = df['title'] + ' ' + df['release_date'] + ' ' + df['overview']
    vectorizer = TfidfVectorizer(lowercase=True, analyzer='word',strip_accents='unicode',stop_words='english')
    combined_features_vec = vectorizer.fit_transform(df['combined_features'])
    movie_to_index = pd.Series(data=df.index, index=df['title']).to_dict()
    recom = []
    movies_idx=[movie_to_index[e] for e in movies]
    for movie_name in movies:
        if movie_name in movie_to_index:
            # Get the index of the movie from its name
            idx = movie_to_index[movie_name]
            # Compute cosine similarity between the movie's features and the features of all movies
            cosine_sim = cosine_similarity(combined_features_vec, combined_features_vec[idx].reshape(1, -1))
            
            # Get pairwise similarity scores for all movies with that movie
            sim_scores = list(enumerate(cosine_sim.flatten()))
            
            # Sort the movies based on the similarity scores
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)    
            
            # Get the scores of the 50 most similar movies, skip the first one since it is the query movie itself
            sim_scores2 = []
            i=0
            for i in range(len(sim_scores)):
                if not sim_scores[i][0] in movies_idx :
                    sim_scores2.append(sim_scores[i])
            movie_indices = [i[0] for i in sim_scores2]
            # Return the top 50 most similar movies
            recom.append(df.iloc[movie_indices]['title'].to_list())
    R = []
    l=len(movies)
    j=0
    i=0
    while len(R)<num_recom:
        if i>=l : j+=1
        if recom[i%l][j] not in R : R.append(recom[i%l][j])
        i+=1
    return R