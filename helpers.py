from functools import wraps
from flask import flash, redirect, session
from passlib.hash import sha256_crypt
from model import db, User

# This file contains a selection of helper functions


# This function gets data from the User table if the username exists 
# and evaluates if the password is correct
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("name"):
            flash("You must be logged in.")
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_logged_in_user_admin():
            flash("Only admins are permitted")
        return f(*args, **kwargs)

    return decorated_function