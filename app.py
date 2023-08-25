from flask import Flask, redirect, render_template, request, session
import sqlite3
from passlib.hash import sha256_crypt


app = Flask(__name__)
app.secret_key = "used for dev"


def create_user_db():
    conn = sqlite3.connect("/users.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_user_db()
    app.run(debug=True)


# load the index
@app.route("/")
def index():
    if request.method == "GET":
        return render_template("index.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Fetch the hashed password
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        hashed_password = cursor.fetchone()

        conn.close()

        # Check if the password provided matches the hash and redirect to the index
        if sha256_crypt.verify(password, hashed_password[0]):
            session["username"] = username
            return redirect("/")
    return render_template("login.html")


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Hash password for security reasons
        hashed_password = sha256_crypt.encrypt(password)

        # Add user to users.db
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password),
        )
        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("register.html")
