from app.model.UserModel import User
from app.extensions import db

def get_all_user():
    return User.query.all()