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
        user = db.session.query(User).get(user_id)
        return [] if not user else list(user.movies)


    def add_movie(self, movie):
        db.session.add(movie)
        db.session.commit()
        return movie


    def update_movie(self, movie_id, new_title):
        movie_to_update = db.session.query(Movie).get(movie_id)
        if not movie_to_update:
            return None
        movie_to_update.title = new_title
        db.session.commit()
        return movie_to_update


    def delete_movie(self, user_id, movie_id):
        movie_to_delete = db.session.query(Movie).get(movie_id)
        user = db.session.query(User).get(user_id)
        if not movie_to_delete or not user or movie_to_delete not in user.movies:
            return None
        user.movies.remove(movie_to_delete)
        if not movie_to_delete.users:
            db.session.delete(movie_to_delete)
        db.session.commit()
        return movie_to_delete


    def delete_user(self, user_id):
        user_to_delete = db.session.query(User).get(user_id)
        if not user_to_delete:
            return None

        for movie in list(user_to_delete.movies):
            user_to_delete.movies.remove(movie)
            if not movie.users:
                db.session.delete(movie)

        db.session.delete(user_to_delete)
        db.session.commit()
        return user_to_delete


    def update_username(self, user_id, new_name):
        user_to_update = db.session.query(User).get(user_id)
        if not user_to_update:
            return None
        user_to_update.name = new_name
        db.session.commit()
        return user_to_update
