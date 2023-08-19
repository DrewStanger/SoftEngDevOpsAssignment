from flask import Flask, render_template, request

app = Flask(__name__)

# load the index
@app.route('/')
def index():
    if request.method == "GET":
        return render_template("index.html")

# Login route
@app.route('/login')
def login():
    if request.method == "GET":
        return render_template("login.html")
    
# Register route
@app.route('/register')
def register():
    if request.method == "GET":
        return render_template("register.html")