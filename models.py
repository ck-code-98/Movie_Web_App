from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

user_movies = db.Table(
    'user_movies',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id', ondelete='CASCADE'), primary_key=True),
    db.UniqueConstraint('user_id', 'movie_id')
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(99), nullable=False)
    movies = db.relationship('Movie', secondary=user_movies, backref='users',
                             cascade='save-update', passive_deletes=True)


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(99), nullable=False)
    director = db.Column(db.String(99))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String)
    __table_args__ = (
        db.UniqueConstraint('title', 'year', name='uq_movie_title_year'),
    )
