from flask import Flask, render_template, request, sqlite3

app = Flask(__name__)


def __init__(self):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
        """
    )
    conn.commit()
    conn.close()


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
@app.route("/register")
def register():
    if request.method == "GET":
        return render_template("register.html")
