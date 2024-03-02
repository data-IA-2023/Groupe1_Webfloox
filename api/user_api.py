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
    return cursor.fetchall()

def fetch_users(cursor):
    cursor.execute("""
    SELECT "user","password","light_mode"
    FROM netfloox_complet.user;
    """)
    return cursor.fetchall()

def fetch_history(cursor):
    cursor.execute("""
    SELECT "user", "movies_seen"
    FROM netfloox_complet.user_history;
    """)
    return cursor.fetchall()

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
    print(d4)
    return d2,d,d3,d4

def create_user(cursor,user,hashed_pwd):
    cursor.execute(f"""
    INSERT INTO netfloox_complet.user ("user","password","light_mode")
    VALUES ('{user}','{hashed_pwd}',FALSE);
    """)


def write_history(cursor,user,movie):
    cursor.execute(f"""
    INSERT INTO netfloox_complet.user_history ("user","movies_seen")
    VALUES ('{user}','{movie}');
    """)

def write_favourite(cursor,user,movie,isliked):
    if isliked : 
        cursor.execute(f"""
        DELETE FROM netfloox_complet.user_liked_movies
        WHERE "user" = '{user}' AND "title" = '{movie}';
        """)
    else :
        cursor.execute(f"""
        INSERT INTO netfloox_complet.user_liked_movies ("user","title")
        VALUES ('{user}','{movie}');
        """)


def change_lightmode(cursor,user,lightmode):
    cursor.execute(f"""
    UPDATE netfloox_complet.user
    SET "light_mode" = {"TRUE" if lightmode == True else "FALSE"}
    WHERE "user" = '{user}';
    """)