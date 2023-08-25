from flask import Flask, redirect, render_template, request
import sqlite3


app = Flask(__name__)


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
@app.route("/login")
def login():
    if request.method == "GET":
        return render_template("login.html")


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # TODO:Hash password for security reasons

        # Add user to users.db
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password),
        )
        conn.commit()
        conn.close()
        return redirect("/login")

    return render_template("register.html")
