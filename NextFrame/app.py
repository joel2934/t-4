# %%
# Importing necessary libraries
import os
import requests

from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from recommend import recommend, movie_data


# %%
# Loading environment variables
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE_URL = "https://api.themoviedb.org/3"

TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


# %%
# Getting movie titles available in recommendation dataset

available_movies = set(
    movie_data["title"].str.lower()
)


# %%
# Creating FastAPI application

app = FastAPI(
    title="NextFrame",
    description="Movie Recommendation System",
    version="1.0"
)


# %%
# Setting templates folder

templates = Jinja2Templates(
    directory="templates"
)


# %%
# Home page

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# %%
# Searching movies using TMDB

@app.get("/search")
def search_movies(query: str):

    url = f"{TMDB_BASE_URL}/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "include_adult": False
    }

    response = requests.get(
        url,
        params=params
    )


    # Checking TMDB response

    if response.status_code != 200:

        return {
            "error": "TMDB API request failed"
        }


    data = response.json()

    movies = []


    # Filtering TMDB results
    # to movies available in ML dataset

    for movie in data.get("results", []):

        title = movie.get("title")


        if not title:

            continue


        # Check whether movie exists
        # in recommendation dataset

        if title.lower() not in available_movies:

            continue


        movies.append({

            "id": movie.get("id"),

            "title": title,

            "release_date":
                movie.get("release_date"),

            "overview":
                movie.get("overview"),

            "rating":
                movie.get("vote_average"),

            "poster": (

                TMDB_IMAGE_URL
                + movie["poster_path"]

                if movie.get("poster_path")

                else None

            )

        })


        # Return maximum 8 movies

        if len(movies) == 8:

            break


    # No compatible movies found

    if len(movies) == 0:

        return {
            "error":
                "No matching movies found in the recommendation dataset."
        }


    return {
        "results": movies
    }


# %%
# Getting movie details from TMDB

def get_tmdb_movie(title):

    url = f"{TMDB_BASE_URL}/search/movie"


    params = {

        "api_key":
            TMDB_API_KEY,

        "query":
            title,

        "include_adult":
            False

    }


    response = requests.get(
        url,
        params=params
    )


    # Checking TMDB response

    if response.status_code != 200:

        return None


    data = response.json()


    results = data.get(
        "results",
        []
    )


    # Movie not found

    if not results:

        return None


    movie = results[0]


    return {

        "id":
            movie.get("id"),

        "title":
            movie.get("title"),

        "overview":
            movie.get("overview"),

        "rating":
            movie.get("vote_average"),

        "release_date":
            movie.get("release_date"),

        "poster": (

            TMDB_IMAGE_URL
            + movie["poster_path"]

            if movie.get("poster_path")

            else None

        )

    }


# %%
# Recommendation API

@app.get("/recommend/{movie}")

def get_recommendations(movie: str):

    try:


        # Getting recommendations
        # from ML model

        recommendations = recommend(movie)


        movies = []


        # Getting TMDB details
        # for every recommendation

        for recommendation in recommendations:


            movie_details = get_tmdb_movie(
                recommendation["title"]
            )


            if movie_details:

                movies.append(
                    movie_details
                )


        return {

            "movie":
                movie,

            "recommendations":
                movies

        }


    except IndexError:


        return {

            "error":
                "Movie not found in recommendation dataset"

        }


    except Exception as e:


        return {

            "error":
                str(e)

        }