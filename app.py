from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

app = Flask(__name__)

 
# Session will use filesystem
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    return render_template("index.html")
