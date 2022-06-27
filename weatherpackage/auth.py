import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from weatherpackage.db import get_db
from sqlalchemy import text, exc


bp = Blueprint("auth", __name__, url_prefix = "/auth")

# Before_app_request makes this load no matter what. That way the user is available to all pages if they're logged in.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(text(
            "SELECT * FROM users WHERE id = :id").bindparams( id = user_id,
        )).fetchone()

# Create the registration view
@bp.route("/register", methods = ("GET", "POST"))
def register():
    if request.method == "POST":

        # Import the database connection as db
        db = get_db()
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
                db.execute(
                    text("INSERT INTO users (username, password_hashed) VALUES (:name, :hashedpass)").bindparams(name = username, hashedpass = generate_password_hash(password))
                )
                # Check for duplicate username 
            except exc.IntegrityError:
                error = f"The username '{username}' is already registered. Please try a different username"
                flash(error, "error")
                return redirect(url_for("auth.register"))
        # Login the user if registration was successful
            user = db.execute(
                text("SELECT * FROM users WHERE username = :name").bindparams(name = username)
            ).fetchone()
            session.clear()
            session["user_id"] = user["id"]
            flash("Registration successful!", "success")
            return redirect(url_for('home'))
        # If registration failed for any reason flash the relevant error and refresh the page
        else:
            flash(error, "error")
            return redirect(url_for("auth.register"))

   # Load page for GET requests
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

        user = db.execute(
            text("SELECT * FROM users WHERE username = :name").bindparams(name = username)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user['password_hashed'], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for('home'))

        flash(error, "error")

    return render_template('auth/login.html')

# Add a logout function
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Creating a decorator that requires login
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view