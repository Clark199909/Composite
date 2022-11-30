from flask_login import UserMixin
from src.resources.user_resource import UserResource


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        dbuser = UserResource.search_user_by_id(user_id)
        if not dbuser:
            return None

        user = User(
            id_=dbuser.id, name=dbuser.name, email=dbuser.email, profile_pic=dbuser.profile_pic
        )
        return user
