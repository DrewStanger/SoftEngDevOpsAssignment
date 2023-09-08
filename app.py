from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import sha256_crypt
from os import path


# configure app
app = Flask(__name__)
app.secret_key = "used for dev"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user_status.db"
Session(app)
# init db
db.init_app(app)


#  define db models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    set_status = db.relationship("UserStatus")


class UserStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    urconst = db.Column(db.String(8), nullable=False)
    status = db.Column(db.String(150), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    setting_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    setting_user_name = db.Column(db.String(20), nullable=False)


def create_database():
    with app.app_context():
        if not path.exists("/user_status.db"):
            db.create_all()
            print("database created")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)


@app.route("/")
def index():
    # Users must login to use the system, check if user is logged in
    if not session.get("name"):
        return redirect("/login")
    return render_template("index.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Fetch the hashed password
        hashed_password = (
            db.session.query(User.password).filter_by(username=username).first()
        )

        # Check if the password provided matches the hash and redirect to the index
        if sha256_crypt.verify(password, hashed_password[0]):
            # Store username in session
            session["name"] = username
            return redirect("/dashboard")
        # TODO: add error messaging, incorrect password? user does not exist?
    # If request.method !== POST, load login page
    return render_template("login.html")


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    # TODO this route will display the table of users who have an assigned status
    user_status = UserStatus.query.with_entities(UserStatus.id, UserStatus.urconst, UserStatus.status, UserStatus.reason, UserStatus.setting_user_id, UserStatus.setting_user_name).all()
    return render_template("dashboard.html", user_status=user_status)


@app.route("/dashboard/add", methods=["GET", "POST"])
def dashboard_add():
    if request.method == "POST":
        urconst = request.form.get("urconst")
        status = request.form.get("status")
        reason = request.form.get("reason")

        # Figure out who the logged in user is and their username
        logged_in_username = session.get("name")
        logged_in_user_id = (
            db.session.query(User.id).filter_by(username=logged_in_username).first()
        )[0]

        # Create a new UserStatus record in the database
        new_status = UserStatus(
            urconst=urconst,
            status=status,
            reason=reason,
            setting_user_id=logged_in_user_id,
            setting_user_name=logged_in_username,
        )

        db.session.add(new_status)
        db.session.commit()
        return render_template("adduserstatus.html")

    return render_template("adduserstatus.html")


@app.route("/adminview")
def adminview():
    # Retrieve user data from the User table (excluding the password)
    users = User.query.with_entities(User.id, User.username, User.is_admin).all()
    # Render the HTML template and pass the user data
    return render_template("adminview.html", users=users)


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Front end validation is inplace to enforce both of these. To capture edge cases
        if username == None or password == None:
            # Prompt user to provide username and password
            error = "You must provide both a username and a password"
            return render_template("register.html", error=error)

        # Usernames must be unique, check if already exists
        is_existing = (
            db.session.query(User.id).filter(User.username == username).first()
        )

        if is_existing:
            # Prompt user to use unique username
            error = f"The username '{username}' already exists, try a different one"
            return render_template("register.html", error=error)
        else:
            # Hash password for security reasons
            hashed_password = sha256_crypt.encrypt(password)

            # Add user to users.db, new users are not admin by default
            new_user = User(username=username, password=hashed_password, is_admin=True)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
    return render_template("register.html")
