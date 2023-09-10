from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from passlib.hash import sha256_crypt
from model import db, User, UserStatus 
from os import path

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

        # If the user exists and provides correct details
        if authenticate_user(username, password):
            return redirect("/dashboard")
        else: 
            error = 'Username or Password is incorrect, please try again.'
            return render_template("login.html", error=error)
    return render_template("login.html")

# This function gets data from the User table if the username exists and evaluates if the password is correct
def authenticate_user(username, password):
    user = db.session.query(User).filter_by(username=username).first()
    if user and sha256_crypt.verify(password, user.password):
        session["name"] = username
        return True
    return False

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    # Get all User Status entries from the db and render these
    user_status = UserStatus.query.with_entities(
        UserStatus.id,
        UserStatus.urconst,
        UserStatus.status,
        UserStatus.reason,
        UserStatus.setting_user_id,
        UserStatus.setting_user_name,
    ).all()
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


@app.route("/edit_status/<int:status_id>", methods=["GET", "POST"])
def edit_user_status(status_id):
    # Retrieve the UserStatus record to edit
    status_to_edit = UserStatus.query.filter_by(id=status_id).first()
    # We also want to show the last person to edit the data
    logged_in_username = session.get("name")
    logged_in_user_id = (
            db.session.query(User.id).filter_by(username=logged_in_username).first()
        )[0]

    if request.method == "POST":
        # Get the updated data from the form
        updated_status = request.form.get("status")
        updated_reason = request.form.get("reason")

        # Update the status data
        status_to_edit.status = updated_status
        status_to_edit.reason = updated_reason
        status_to_edit.setting_user_name = logged_in_username
        status_to_edit.setting_user_id = logged_in_user_id

        # Commit the changes to the database
        db.session.commit()

        # Redirect the user back to the dashboard
        return redirect("/dashboard")

    # Render the edit form with pre-filled data
    return render_template("edit_status.html", status_to_edit=status_to_edit)

@app.route("/delete_status/<int:status_id>", methods=["GET", "POST"])
def delete_user_status(status_id):
    logged_in_username = session.get("name")
    is_user_admin = (
        db.session.query(User.is_admin).filter_by(username=logged_in_username).first()
    )[0]

    if is_user_admin == True:
        # Get the entry to delete
        status_to_delete = UserStatus.query.filter_by(id=status_id).first()
        db.session.delete(status_to_delete)
        db.session.commit()
        return redirect("/dashboard")
    else:
        error = "Delete failed: only Admins can delete entries"
        return render_template("dashboard.html", error=error)

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_staff_perms(user_id):
    # Retrieve the UserStatus record to edit
    user_to_edit = User.query.filter_by(id=user_id).first()

    if request.method == "POST":
        # Get the updated data from the form
        updated_username = request.form.get("username")
        updated_admin_status = request.form.get("is_admin")


        # Update the status data
        user_to_edit.username = updated_username
        user_to_edit.updated_admin_status = updated_admin_status

        # Commit the changes to the database
        db.session.commit()

        # Redirect the user back to the dashboard
        return redirect("/adminview")

    # Render the edit form with pre-filled data
    return render_template("edit_user_perms.html", user_to_edit=user_to_edit)

@app.route("/delete_user/<int:user_id>", methods=["GET", "POST"])
def delete_staff_perms(user_id):    
    logged_in_username = session.get("name")
    # User should not be able to delete themselves
    user_name_to_delete = (
            db.session.query(User.username).filter_by(id=user_id).first()
        )[0]
    
    if logged_in_username == user_name_to_delete: 
        print(logged_in_username)
        print(user_name_to_delete)
        error = "User cannot remove their own permissions, contact an Admin"
        return render_template("/adminview.html", error=error)

    # User must be admin to delete
    is_user_admin = (
            db.session.query(User.is_admin).filter_by(username=logged_in_username).first()
        )[0]

    if is_user_admin == True:
        # Get the entry to delete
        user_to_delete = db.session.query(User).filter_by(id=user_id).first()
        db.session.delete(user_to_delete)
        db.session.commit()
        return render_template("/adminview.html")
    else:
        error = "Delete failed: only Admins can delete entries"
        return render_template("/adminview.html", error=error)


@app.route("/adminview")
def display_user_perms():
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
            new_user = User(username=username, password=hashed_password, is_admin=False)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")
    return render_template("register.html")
