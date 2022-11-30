from src import db
from src.models.dbuser import DBUser


class UserResource:
    def __int__(self):
        pass

    @staticmethod
    def search_user_by_id(user_id):
        return db.session.query(DBUser).filter_by(id=user_id).first()

    @staticmethod
    def save_user(user_id, name, email, profile_pic):
        user = DBUser(id=user_id, name=name, email=email, profile_pic=profile_pic)
        db.session.add(user)
        db.session.commit()
