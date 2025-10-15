from flask import Flask, request, render_template, redirect, url_for, flash
from data_manager import DataManager
from models import db, Movie
from dotenv import load_dotenv
import os
import requests


load_dotenv(dotenv_path="config/.env")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
OMDB_API_URL_BASE = "https://www.omdbapi.com/"

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
data_manager = DataManager()


@app.route('/')
def index():
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    name = request.form.get("name", "").strip()
    data_manager.create_user(name)

    flash("User created successfully!")
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', user_id=user_id, movies=movies)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    title = request.form['title']
    response = requests.get(OMDB_API_URL_BASE,
                        params={'t': title, 'apikey': OMDB_API_KEY}, timeout=10)
    response.raise_for_status()
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
    flash("Movie added successfully!")
    return redirect(url_for("get_movies", user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie_title(user_id, movie_id):
    new_title = request.form.get("title", "").strip()
    if not new_title:
        flash("Title cannot be empty!")
        return redirect(url_for("get_movies", user_id=user_id))
    updated_movie = data_manager.update_movie(movie_id, new_title)
    flash(f"Movie {updated_movie.title} updated successfully!")
    return redirect(url_for("get_movies", user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    deleted_movie = data_manager.delete_movie(movie_id)
    flash(f"Movie {deleted_movie.title} deleted successfully!")
    return redirect(url_for("get_movies", user_id=user_id))


if __name__ == "__main__":
#    with app.app_context():
#        db.create_all()
    app.run()
