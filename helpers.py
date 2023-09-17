from flask import session
from os import path
from passlib.hash import sha256_crypt
from model import db, User
from app import app

# This file contains a selection of helper functions


def create_database():
    with app.app_context():
        if not path.exists("/user_status.db"):
            db.create_all()
            print("database created")


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
    return (db.session.query(User.id).filter_by(username=logged_in_username).first())[0]
