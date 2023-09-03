from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from passlib.hash import sha256_crypt

# configure app
app = Flask(__name__)
app.secret_key = "used for dev"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def create_user_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            isAdmin BOOLEAN NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_status (
            urconst INTEGER PRIMARY KEY,
            status TEXT NOT NULL,
            reason TEXT NOT NULL,
            setting_user_id INTEGER NOT NULL
            setting_username TEXT NOT NULL 
            FOREIGN KEY (setting_user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_user_db()
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

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Fetch the hashed password, using ? prevents SQL injections
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        hashed_password = cursor.fetchone()

        conn.close()

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
    # TODO DISPLAY THE LIST OF USERS IN THE USER_STATUS TABLE
    conn = sqlite3.connect("user_status.db")
    cursor = conn.cursor()

    # Fetch the hashed password, using ? prevents SQL injections
    data = cursor.execute("SELECT * FROM user_status")
    conn.close()

    # TODO: table data
    table_data = []
    for entry in data:
        # urconst= entry.urconst
        # status= entry.status
        # reason= entry.reason
        # set_by= entry.set_by
        # user_id= entry.user_id
        table_data.append(entry) 

    return render_template("dashboard.html", table_data=table_data)


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

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Usernames must be unique, check if already exists
        is_existing = cursor.execute(
            "SELECT id FROM users WHERE username=?",
            [username],
        )
        if is_existing:
            # Prompt user to use unique username
            error = f"The username '{username}' already exists, try a different one"
            return render_template("register.html", error=error)
        else:
            # Hash password for security reasons
            hashed_password = sha256_crypt.encrypt(password)

            # Add user to users.db
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password),
            )
            conn.commit()
            conn.close()
            return redirect("/login")

    return render_template("register.html")

