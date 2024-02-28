from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras 
import pandas as pd
import requests
from datetime import datetime
from calendar import monthrange
import os

app = Flask(__name__)
app.secret_key = 'A2310!'

def fetch_current_month_movies_to_df_with_posters(api_key):
    base_url = "https://api.themoviedb.org/3"
    image_base_url = "https://image.tmdb.org/t/p/w500"  # Base URL for images
    
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    
    start_date = f"{year}-{month:02d}-01"
    end_of_month_day = monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{end_of_month_day}"
    
    discover_url = f"{base_url}/discover/movie?api_key={api_key}&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}"
    
    response = requests.get(discover_url)
    if response.status_code != 200:
        return pd.DataFrame()  # Return an empty DataFrame if the request failed

    movies = response.json().get('results', [])
    
    movie_details_list = []
    for movie in movies:
        poster_url = f"{image_base_url}{movie['poster_path']}" if movie.get('poster_path') else None
        
        movie_details_list.append({
            'title': movie.get('title'),
            'release_date': movie.get('release_date'),
            'poster_url': poster_url,
            'overview': movie.get('overview')
        })
    
    df = pd.DataFrame(movie_details_list)
    return df

@app.route("/")
def read_root():
    api_key = os.getenv('TMDB_API_KEY', 'b7cd3340a794e5a2f35e3abb820b497f')  # Environment variable or default
    df = fetch_current_month_movies_to_df_with_posters(api_key)
    movies_list = df.to_dict(orient="records") if not df.empty else []
    return render_template("index.html", movies=movies_list)


def get_db_connection():
    username = 'postgres'   
    password = 'A2310'   
    hostname = 'localhost'    
    db = 'netfloox' 
    sslmode = "require"
    conn_string = f"host={hostname} dbname={db} user={username} password={password} sslmode={sslmode}"
    conn = psycopg2.connect(conn_string)
    return conn

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute('SELECT * FROM users;')
    users = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([dict(user) for user in users]), 200

@app.route('/signup', methods=['GET', 'POST'])

def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password_hash, email))
            conn.commit()
            flash('Signup successful. Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()  # Rollback in case of error
            flash('Signup failed. Please try again.')
            print(e)  # For debugging purpose
        finally:
            cur.close()
            conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']  # Start the session
                session['username'] = username  # Optionally, store the username or other details
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password')
        except Exception as e:
            flash('An error occurred. Please try again.')
            print(e)
        finally:
            cur.close()
            conn.close()
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user_id from session
    session.pop('username', None)  # Optionally remove other stored details
    return redirect(url_for('/index'))

@app.route('/home')
def home():
    return 'Welcome! You are logged in.'

@app.route('/index')
def index():
    return render_template('index.html')





if __name__ == '__main__':
    
    app.run(debug=True)
