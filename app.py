from functools import wraps
from os import path
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_bootstrap import Bootstrap
from passlib.hash import sha256_crypt
from forms import (
    AddUserStatusForm,
    DashboardForm,
    AdminViewForm,
    EditStatusForm,
    EditUserPermsForm,
    LoginForm,
    RegistrationForm,
)
from model import db, User, UserStatus
from helpers import *
from distutils.util import strtobool
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import escape

# configure app
app = Flask(__name__)
app.secret_key = "used for dev"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user_status.db"
Session(app)
Bootstrap(app)
# init db
db.init_app(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)


def create_database():
    with app.app_context():
        if not path.exists("/user_status.db"):
            db.create_all()
            print("database created")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)


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


@app.route("/")
def index():
    # Users must login to use the system, check if user is logged in
    if not session.get("name"):
        return redirect("/login")
    return render_template("index.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = escape(request.form.get("username"))
        password = escape(request.form.get("password"))

        # If the user exists and provides correct details
        if authenticate_user(username, password):
            return redirect("/dashboard")
        else:
            flash("Username or Password is incorrect, please try again.")
            return redirect("/login")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


@app.route("/dashboard")
@login_required
def dashboard():
    form = DashboardForm()
    # Get all User Status entries from the db and render these
    user_status = UserStatus.query.with_entities(
        UserStatus.id,
        UserStatus.urconst,
        UserStatus.status,
        UserStatus.reason,
        UserStatus.setting_user_id,
        UserStatus.setting_user_name,
    ).all()
    return render_template("dashboard.html", user_status=user_status, form=form)


@app.route("/dashboard/add", methods=["GET", "POST"])
@login_required
def dashboard_add():
    form = AddUserStatusForm()
    if form.validate_on_submit():
        urconst = escape(form.urconst.data)
        status = escape(form.status.data)
        reason = escape(form.reason.data)

        # Figure out who the logged in user is and their username
        logged_in_username = escape(session.get("name"))
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
        flash(f"Entry for {urconst} has successfully been added!")
        return redirect("/dashboard/add")

    return render_template("adduserstatus.html", form=form)


@app.route("/edit_status/<int:status_id>", methods=["GET", "POST"])
@login_required
def edit_user_status(status_id):
    # Retrieve the UserStatus record to edit
    status_to_edit = UserStatus.query.filter_by(id=status_id).first()

    form = EditStatusForm()

    if form.validate_on_submit():
        # Get the updated data from the form
        status_to_edit.status = escape(form.status.data)
        status_to_edit.reason = escape(form.reason.data)
        # We also want to show the last person to edit the data
        logged_in_username = escape(session.get("name"))
        status_to_edit.setting_user_name = logged_in_username
        status_to_edit.setting_user_id = (
            db.session.query(User.id).filter_by(username=logged_in_username).first()[0]
        )

        # Commit the changes to the database
        db.session.commit()

        # Redirect the user back to the dashboard
        flash(f"Status successfully updated for {status_to_edit.urconst}")
        return redirect("/dashboard")

    # Pre-fill the form with existing data
    form.status.data = escape(status_to_edit.status)
    form.reason.data = escape(status_to_edit.reason)

    # Render the edit form with pre-filled data
    return render_template("edit_status.html", form=form, status_to_edit=status_to_edit)


@app.route("/delete_status/<int:status_id>", methods=["GET", "POST"])
@login_required
@admin_only
def delete_user_status(status_id):
    form = DashboardForm()
    if form.validate_on_submit():
        # Get the entry to delete
        status_to_delete = UserStatus.query.filter_by(id=status_id).first()
        db.session.delete(status_to_delete)
        db.session.commit()

        flash(f"Status successfully deleted for {status_to_delete.urconst}")
        return redirect("/dashboard")
    else:
        flash(
            "Delete failed: only Admins can delete entries. Set it to Neutral instead."
        )
        return redirect("/dashboard")


@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_staff_perms(user_id):
    # Retrieve the UserStatus record to edit
    user_to_edit = User.query.filter_by(id=user_id).first()

    form = EditUserPermsForm()

    if form.validate_on_submit():
        if is_logged_in_user_admin() == True:
            # Get the updated data from the form
            updated_admin_status = escape(request.form.get("is_admin"))

            # Safely convert string value to Boolean in a manner python can understand
            user_to_edit.is_admin = strtobool(updated_admin_status)

            # Commit the changes to the database
            db.session.commit()

            # Redirect the user back to the dashboard
            flash(f"User Admin status succesfully updated")
            return redirect("/adminview")
        else:
            flash(f"Only Admins are permitted to update this section")
            return redirect("/adminview")

    # Pre-fill the form with existing data
    form.is_admin.data = user_to_edit.is_admin
    # Render the edit form with pre-filled data
    return render_template("edit_user_perms.html", form=form, user_to_edit=user_to_edit)


@app.route("/delete_user/<int:user_id>", methods=["GET", "POST"])
@login_required
def delete_staff_perms(user_id):
    form = AdminViewForm()
    if form.validate_on_submit:
        logged_in_username = escape(session.get("name"))
        # User should not be able to delete themselves
        user_name_to_delete = (
            db.session.query(User.username).filter_by(id=user_id).first()
        )[0]

        if logged_in_username == user_name_to_delete:
            flash("User cannot remove their own permissions, contact an Admin")
            return redirect("/adminview")

        # Only admins can delete users
        if is_logged_in_user_admin() == True:
            # Get the entry to delete
            user_to_delete = db.session.query(User).filter_by(id=user_id).first()
            db.session.delete(user_to_delete)
            db.session.commit()
            flash(f"Succesfully deleted user {user_to_delete.username}")
            return redirect("/adminview")
        else:
            flash("Delete failed: only Admins can delete entries")
            return redirect("/adminview")


@app.route("/adminview")
@login_required
def display_user_perms():
    form = AdminViewForm()
    # Retrieve user data from the User table (excluding the password)
    users = User.query.with_entities(User.id, User.username, User.is_admin).all()
    # Render the HTML template and pass the user data
    return render_template("adminview.html", users=users, form=form)


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = escape(request.form.get("username"))
        password = escape(request.form.get("password"))

        # Front end validation is inplace to enforce both of these. To capture edge cases
        if username == None or password == None:
            # Prompt user to provide username and password
            flash("You must provide both a username and a password")
            return redirect("/register")

        # Usernames must be unique, check if already exists
        is_existing = (
            db.session.query(User.id).filter(User.username == username).first()
        )

        if is_existing:
            # Prompt user to use unique username
            flash(f"The username '{username}' already exists, try a different one")
            return redirect("/register")
        else:
            # Hash password for security reasons
            hashed_password = sha256_crypt.encrypt(password)

            # Add user to users.db, new users are not admin by default
            new_user = User(username=username, password=hashed_password, is_admin=False)
            db.session.add(new_user)
            db.session.commit()
            flash("You successfully Registered!")
            return redirect("/login")
    return render_template("register.html", form=form)
