from flask import session
from passlib.hash import sha256_crypt
from model import db, User

# This file contains a selection of helper functions


# This function gets data from the User table if the username exists and evaluates if the password is correct
def authenticate_user(username, password):
    user = db.session.query(User).filter_by(username=username).first()
    if user and sha256_crypt.verify(password, user.password):
        session["name"] = username
        return True
    return False


# Function returns True if user is admin, false if not
def is_logged_in_user_admin():
    logged_in_username = session.get("name")
    user = User.query.filter_by(username=logged_in_username).first()
    if user:
        return user.is_admin
    else:
        return False
