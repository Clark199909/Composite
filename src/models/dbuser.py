from src import db


class DBUser(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    profile_pic = db.Column(db.String(255), nullable=False)

