from imports2 import *

def fetch_current_month_movies_to_df_with_posters(api_key):
    base_url = "https://api.themoviedb.org/3"
    image_base_url = "https://image.tmdb.org/t/p/w500"  # Base URL for images
    
    current_date = datetime.datetime.now()
    year = current_date.year
    month = current_date.month
    
    start_date = f"{year}-01-01"
    end_of_month_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{end_of_month_day}"
    
    #discover_url = f"{base_url}/discover/movie?api_key={api_key}&primary_release_date.gte={start_date}&primary_release_date.lte={end_date}"
    movies=[]
    for i in range(1,501):
        discover_url = f"{base_url}/discover/movie?api_key={api_key}&include_adult=false&include_video=false&language=en-US&page={i}&sort_by=popularity.desc"
        response = requests.get(discover_url)
        if response.status_code != 200:
            pass
        else :
            movies=movies+response.json().get('results', [])
        discover_url = f"{base_url}/discover/tv?api_key={api_key}&include_adult=false&include_null_first_air_dates=false&language=en-US&page=1&sort_by=popularity.desc"
        response = requests.get(discover_url)
        if response.status_code != 200:
            pass 
        else :
            movies=movies+response.json().get('results', [])
    if len(movies)==0 : return pd.DataFrame()
    movie_details_list = []
    for movie in movies:
        poster_url = f"{image_base_url}{movie['poster_path']}" if movie.get('poster_path') else None
        
        movie_details_list.append({
            'title': movie.get('title'),
            'release_date': movie.get('release_date'),
            'poster_url': poster_url,
            'overview': movie.get('overview')
        })
    
    df = pd.DataFrame(movie_details_list).drop_duplicates(subset=["title"]).dropna()
    return df
