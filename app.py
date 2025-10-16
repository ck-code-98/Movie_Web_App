from flask import Flask, request, render_template, redirect, url_for, flash
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from data_manager import DataManager
from models import db, Movie, User
from dotenv import load_dotenv
import os
import requests


load_dotenv(dotenv_path="config/.env")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
OMDB_API_URL_BASE = "https://www.omdbapi.com/"

if not OMDB_API_KEY:
    raise RuntimeError("Missing Key for OMDb API")

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
    if not name:
        flash("Name required", "error")
        return redirect(url_for('index'))

    data_manager.create_user(name)
    flash("User created successfully!", "success")
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found!", "error")
        return redirect(url_for('index'))
    movies = user.movies
    return render_template('movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    title = " ".join(request.form.get("title", "").split())
    if not title:
        flash("Title cannot be empty!", "error")
        return redirect(url_for("get_movies", user_id=user_id))

    user = db.session.get(User, user_id)
    if not user:
        flash("User not found!", "error")
        return redirect(url_for('index'))

    try:
        response = requests.get(OMDB_API_URL_BASE,
                                params={'t': title, 'apikey': OMDB_API_KEY}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.Timeout:
        flash("OMDb Timeout. Please try again.", "error")
        return redirect(url_for("get_movies", user_id=user_id))
    except requests.RequestException:
        flash("OMDb currently not available. Please try again later.", "error")
        return redirect(url_for("get_movies", user_id=user_id))

    if data.get('Response') == 'False':
        flash(f"Movie '{title}' not found!", "error")
        return redirect(url_for("get_movies", user_id=user_id))

    title = data.get('Title', title)
    director = None if data.get('Director') in (None, 'N/A') else data['Director']
    poster_url = None if data.get('Poster') in (None, 'N/A') else data['Poster']
    year_str = data.get('Year')
    try:
        year = int(year_str) if year_str else None
    except ValueError:
        year = None

    movie = db.session.query(Movie).filter(
        func.lower(Movie.title) == func.lower(title),
        Movie.year == year
    ).first()

    if not movie:
        movie = Movie(title=title, director=director, year=year, poster_url=poster_url)
        db.session.add(movie)
        db.session.commit()

    if movie in user.movies:
        flash(f"The Movie '{title}' is already in your movie list!", "error")
        return redirect(url_for("get_movies", user_id=user_id))

    user.movies.append(movie)
    db.session.commit()
    flash("Movie added successfully!", "success")
    return redirect(url_for("get_movies", user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie_title(user_id, movie_id):
    new_title = request.form.get("title", "").strip()
    if not new_title:
        flash("Title cannot be empty!", "error")
        return redirect(url_for("get_movies", user_id=user_id))

    updated_movie = data_manager.update_movie(movie_id, new_title)
    if not updated_movie:
        flash("Movie not updated!", "error")
        return redirect(url_for("get_movies", user_id=user_id))
    flash(f"Movie {updated_movie.title} updated successfully!", "success")
    return redirect(url_for("get_movies", user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    deleted = data_manager.delete_movie(user_id, movie_id)
    if not deleted:
        flash("Movie not deleted!", "error")
    else:
        flash(f"Movie {deleted.title} deleted successfully!", "success")

    return redirect(url_for("get_movies", user_id=user_id))


@app.route('/users/<int:user_id>/update', methods=['POST'])
def update_username(user_id):
    new_name = request.form.get("name", "").strip()
    if not new_name:
        flash("Name cannot be empty!", "error")
        return redirect(url_for("index"))

    updated_user = data_manager.update_username(user_id, new_name)
    if not updated_user:
        flash("User not updated!", "error")
        return redirect(url_for("index"))
    flash(f"Username updated successfully!", "success")
    return redirect(url_for("index"))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    deleted_user = data_manager.delete_user(user_id)
    if not deleted_user:
        flash(f"User not deleted!", "error")
    else:
        flash(f"User {deleted_user.name} deleted successfully!", "success")
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(SQLAlchemyError)
def handle_db_error(e):
    db.session.rollback()
    flash("A database error occurred!", "error")
    return render_template('500.html'), 500


if __name__ == "__main__":
#    with app.app_context():
#        db.create_all()
    app.run()
