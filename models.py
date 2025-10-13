from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(99), nullable=False)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(99), nullable=False)
    director = db.Column(db.String(99))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user_id'), nullable=False)

