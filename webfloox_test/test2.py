from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from boxoffice_api import BoxOffice  # Ensure this is correctly imported based on your actual setup
import os
from fastapi.staticfiles import StaticFiles
app = FastAPI()
templates = Jinja2Templates(directory="templates")

OMDB_API_KEY ="bc442c47"

import requests
def get_movie_details(title):
    """Fetch movie details including the poster from OMDB API by title."""
    # Correctly format the URL with the query parameters
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code.
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

@app.get("/")
async def read_root(request: Request):
    current_date = datetime.now()
    one_month_earlier = current_date - relativedelta(day=2)
    date = one_month_earlier.strftime('%Y-%m-%d')
    
    # Assuming BoxOffice API setup is similar and correct
    box_office = BoxOffice(api_key="bc442c47")
    box_office_data = box_office.get_daily(date)

    movies_df = pd.DataFrame(box_office_data)
    
    # Fetch movie details from OMDB for each movie
    movies_details = [get_movie_details(title) for title in movies_df['Title']]
    
    movies_df = pd.DataFrame(movies_details)
    
    return templates.TemplateResponse("index.html", {"request": request, "movies": movies_df.to_dict(orient='records')})

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
