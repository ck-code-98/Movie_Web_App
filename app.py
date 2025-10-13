from flask import Flask, request
from data_manager import DataManager
from models import db, Movie
import os
from dotenv import load_dotenv
import requests

load_dotenv(dotenv_path="config/.env")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
OMDB_API_URL_BASE = "http://www.omdbapi.com/"

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
data_manager = DataManager()

"""
@app.route('/users')
def list_users():
    users = data_manager.get_users()
    return str(users)
"""

@app.route('/')
def home():
    return "Welcome to the Movie Web App!"


@app.route('/users', methods=['POST'])
def add_user():
    pass


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def show_favourite_movies(user_id):
    pass


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    title = request.form['title']
    response = requests.get(OMDB_API_URL_BASE,
                        params={'t': title, 'apikey': OMDB_API_KEY})
    data = response.json()

    if data.get('Response') == 'False':
        return f"Movie '{title}' not found!", 404

    title = data.get('Title', title)
    director = None if data.get('Director') in (None, 'N/A') else data['Director']
    poster_url = None if data.get('Poster') in (None, 'N/A') else data['Poster']
    year_str = data.get('Year')
    year = int(year_str) if year_str and year_str.isdigit() else None

    movie = Movie(title=title, director=director, year=year,
                  poster_url=poster_url, user_id=user_id)

    data_manager.add_movie(movie)
    return "Movie added successfully!"


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie_title(user_id, movie_id):
    pass


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(movie_id):
    pass


if __name__ == "__main__":
#    with app.app_context():
#        db.create_all()
    app.run()
