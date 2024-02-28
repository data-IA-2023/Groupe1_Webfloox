
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import pandas as pd
from calendar import monthrange
import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from passlib.context import CryptContext

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")  # Assuming you have a 'static' directory for CSS/JS

def fetch_current_month_movies_to_df_with_posters(api_key):
    base_url = "https://api.themoviedb.org/3"
    image_base_url = "https://image.tmdb.org/t/p/w500"  # Base URL for images
    
    current_date = datetime.datetime.now()
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

api_key = 'b7cd3340a794e5a2f35e3abb820b497f'  # Make sure to replace 'your_api_key_here' with your actual TMDB API key.

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    df = fetch_current_month_movies_to_df_with_posters(api_key)
    movies_list = df.to_dict(orient="records") if not df.empty else []
    return templates.TemplateResponse("index.html", {"request": request, "movies": movies_list})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/signin", response_class=HTMLResponse)
async def get_signin(request: Request):
    return templates.TemplateResponse("./signin.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def get_signup(request: Request):
    return templates.TemplateResponse("./signup.html", {"request": request})


import schemas
import models
from models import User
from database import Base, engine, SessionLocal
from fastapi import FastAPI, Depends, HTTPException,status
from sqlalchemy.orm import Session
Base.metadata.create_all(engine)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
@app.post("/register")
def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password =get_hashed_password(user.password)

    new_user = models.User(username=user.username, email=user.email, password=encrypted_password )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message":"user created successfully"}