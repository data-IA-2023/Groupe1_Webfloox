from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
# Assuming BoxOffice is a custom library you're using
from boxoffice_api import BoxOffice
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")


OMDB_API_KEY =  "bc442c47"

def get_movie_details(title):
    """Fetch movie details including the poster from OMDB API by title."""
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        movie = response.json()

        if movie.get("Response") == "True":
            return {
                "title": movie.get("Title"),
                "poster": movie.get("Poster"),
                "box_office": movie.get("BoxOffice"),
                "release_date": movie.get("Released")
            }
        else:
            return {
                "title": title,
                "poster": None,
                "box_office": "N/A",
                "release_date": "N/A"
            }
    except requests.RequestException as e:
        print(f"Error fetching details for {title}: {e}")
        return {
            "title": title,
            "poster": None,
            "box_office": "N/A",
            "release_date": "N/A"
        }

@app.get("/")
async def read_root(request: Request):
    # Initialize and configure your BoxOffice API client
    box_office = BoxOffice(api_key="bc442c47") 
    box_office = BoxOffice(outputformat="DF") # Example, adjust according to your actual API setup
    # Assuming get_quarterly is a method to fetch data for a specific quarter of a year
    box_office_data = box_office.get_quarterly(1, 2024)
    movies_df = pd.DataFrame(box_office_data).head(20)
    
    # Fetch movie details from OMDB for each movie
    movies_details = [get_movie_details(title) for title in movies_df['Release']]
    
    movies_df = pd.DataFrame(movies_details)
    movies_df = movies_df[movies_df['title'] != 'Mean Girls']
    movies_df = movies_df[movies_df['release_date'] != 'N/A']
    movies_df = movies_df[movies_df['box_office'] != 'N/A']
    movies_df
    return templates.TemplateResponse("movies.html", {"request": request, "movies": movies_df.to_dict(orient='records')})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
