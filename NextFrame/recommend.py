# %%
# Importing necessary libraries
import pandas as pd

# %%
# Reading movies file
movies = pd.read_csv("tmdb_5000_movies.csv")
# %%
# Reading credits file
credits = pd.read_csv("tmdb_5000_credits.csv")
# %%
# Displaying the first few rows of movies dataset
movies.head()
# %%
# Movies dataset information
movies.info()
# %%
# Movies dataset statistics
movies.describe()
# %%
# Movies dataset shape
movies.shape
# %%
# Displaying the first few rows of credits dataset
credits.head()
# %%
# Credits dataset information
credits.info()
# %%
# Credits dataset statistics and shape
credits.describe()
credits.shape
# %%
movies[['id', 'title']].head()
# %%
# %%
credits[['movie_id', 'title']].head()
# %%
# Merging both datasets using movie title
movie_data = movies.merge(
    credits,
    on='title'
)
# %%
# Selecting only the columns needed for recommendation system
movie_data = movie_data[
    [
        'id',
        'title',
        'overview',
        'genres',
        'keywords',
        'cast',
        'crew'
    ]
]
# %%
movie_data.head()
# %%
movie_data.shape
# %%
# Removing rows containing missing values
movie_data.dropna(inplace=True)
# %%
movie_data.isnull().sum()
# %%
import ast

movie_data['genres'] = movie_data['genres'].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
)

movie_data['keywords'] = movie_data['keywords'].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
)

movie_data['cast'] = movie_data['cast'].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
)

movie_data['crew'] = movie_data['crew'].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else x
)
# %%
def get_names(items):
    l = []

    for i in items:
        l.append(i['name'])

    return l
# %%
movie_data['genres'] = movie_data['genres'].apply(get_names)
movie_data['keywords'] = movie_data['keywords'].apply(get_names)

# %%
def get_cast(cast):
    l = []
    counter = 0

    for i in cast:
        if counter != 3:
            l.append(i['name'])
            counter += 1
        else:
            break

    return l

# %%
movie_data['cast'] = movie_data['cast'].apply(get_cast)


def get_director(crew):
    l = []

    for i in crew:
        if i['job'] == 'Director':
            l.append(i['name'])
            break

    return l


movie_data['crew'] = movie_data['crew'].apply(get_director)

# %%
def collapse(lst):
    l = []

    for i in lst:
        l.append(i.replace(" ", ""))

    return l

# %%
movie_data['cast'] = movie_data['cast'].apply(collapse)
movie_data['crew'] = movie_data['crew'].apply(collapse)
movie_data['genres'] = movie_data['genres'].apply(collapse)
movie_data['keywords'] = movie_data['keywords'].apply(collapse)

movie_data[['title', 'genres', 'keywords', 'cast', 'crew']].head()

# %%
def split_overview(text):
    l = text.split()
    return l
# %%
movie_data['overview'] = movie_data['overview'].apply(split_overview)
# %%
# %%
movie_data[['title', 'overview']].head()
# %%
movie_data.columns
# %%
movie_data.sample(5)
# %%
movie_data['tags'] = movie_data.apply(
    lambda row: row['overview'] + row['genres'] + row['keywords'] + row['cast'] + row['crew'],
    axis=1
)
# %%
movie_data[['title', 'tags']].head()

# %%
movie_data['tags'] = movie_data['tags'].apply(
    lambda x: " ".join(x)
)

# %%
movie_data[['title', 'tags']].head()

# %%
from sklearn.feature_extraction.text import CountVectorizer

# %%
cv = CountVectorizer(
    max_features=5000,
    stop_words='english'
)
# %%
vectors = cv.fit_transform(movie_data['tags']).toarray()

# %%
vectors.shape

# %%
from sklearn.metrics.pairwise import cosine_similarity

# %%
similarity = cosine_similarity(vectors)

# %%
similarity.shape
# %%
similarity[0]

# %%
def recommend(movie):

    index = movie_data[
        movie_data['title'] == movie
    ].index[0]

    distances = similarity[index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )

    recommendations = []

    for i in movies_list[1:6]:

        title = movie_data.iloc[i[0]]['title']

        print(title)

        recommendations.append({
            "title": title,
            "id": int(movie_data.iloc[i[0]]['id'])
        })

    return recommendations

# %%