import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from weatherpackage.db import get_db
from flask_sqlalchemy import SQLAlchemy

bp = Blueprint("auth", __name__, url_prefix = "/auth")

# Before_app_request makes this load no matter what. That way the user is available to all pages if they're logged in.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        connection = db.engine.connect()
        g.user = connection.execute(db.text(
            "SELECT * FROM user WHERE id = :id"), id = user_id,
        ).fetchone()

# Create the registration view
@bp.route("/register", methods = ("GET", "POST"))
def register():
    if request.method == "POST":

        # Import the SQLAlchemy object as db and set up a database connection
        db = get_db()
        connection = db.engine.connect()
        # Get the username and password from the registration form and set up an error check
        username = request.form["username"]
        password = request.form["password"]
        error = None
        # Check that the username and password were both submitted.
        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        # If both username and password were submitted, try to insert into database along with the lowercase username.
        if error is None:
            try:
                connection.execute(
                    db.text("INSERT INTO users VALUES (:name, :hashedpass, :check)", name = username, hashedpass = generate_password_hash(password), check = username.lower())
                )
            # Check for duplicate username (username check will catch for case nonsense)
            except db.IntegrityError:
                error = f"User {username} is already registered."
        # Otherwise flash the relevent error on screen and refresh the page
        else:
            flash(error)
            return redirect(url_for("auth.login"))

    # Login will force users to the registration view if they're not logged in.
    else:
        return render_template("auth/register.html")

#Create the Login  View
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # Get the username and password from the registration form and set up an error check
        username = request.form['username']
        password = request.form['password']
        error = None

        # Import the SQLAlchemy object as db and set up a database connection
        db = get_db()
        connection = db.engine.connect()

        user = connection.execute(
            db.text("SELECT * FROM user WHERE username = :name", name = username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

# Add a logout function
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Creating a decorator that requires login
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view