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

def super_function(cursor,conn):

    fetch_user_favs(cursor)

    result = cursor.fetchall()

    d={}
    for e in result:
        d[e[0]]=[]

    for e in result:
        if d[e[0]] != None : d[e[0]]=d[e[0]] + [e[1]]


    def fetch_users(cursor):
        cursor.execute("""
        SELECT "user","password","light_mode"
        FROM netfloox_complet.user;
        """)
    
    def fetch_history(cursor):
        cursor.execute("""
        SELECT "user", "movies_seen"
        FROM netfloox_complet.user_history;
        """)

    fetch_users(cursor)

    result = cursor.fetchall()

    d2={}
    for e in result:
        d2[e[0]]=e[1]

    d3={}
    for e in result:
        d3[e[0]]=e[2]


    fetch_history(cursor)

    result = cursor.fetchall()

    d4={}
    for e in result:
        d4[e[0]]=[]

    for e in result:
        if d4[e[0]] != None : d4[e[0]]=d4[e[0]] + [e[1]]
    
    return d2,d,d3,d4