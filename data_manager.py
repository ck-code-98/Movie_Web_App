from models import db, User, Movie

class DataManager():


    def create_user(self, name):
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user


    def get_users(self):
        list_of_users = db.session.query(User).all()
        return list_of_users


    def get_movies(self, user_id):
        list_of_movies = (db.session.query(Movie)
                          .filter_by(user_id=user_id).all())
        return list_of_movies


    def add_movie(self, movie):
        db.session.add(movie)
        db.session.commit()


    def update_movie(self, movie_id, new_title):
        movie_to_update = db.session.query(Movie).get(movie_id)
        if movie_to_update:
            movie_to_update.title = new_title
            db.session.commit()
            return movie_to_update
        else:
            return None


    def delete_movie(self, movie_id):
        movie_to_delete = db.session.query(Movie).get(movie_id)
        if movie_to_delete:
            db.session.delete(movie_to_delete)
            db.session.commit()
            return movie_to_delete
        else:
            return None
