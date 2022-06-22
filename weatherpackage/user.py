import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from weatherpackage.db import get_db
from sqlalchemy import text, exc

bp = Blueprint("user", __name__, url_prefix = "/user")


# Profile view
@bp.route("/profile", methods = ("GET", "POST"))
def profile():
    # For now if they manage to submit something to this just redirect 'em to the GET option
    if request.method == "POST":
        return redirect(url_for("user.profile"))
    else:
        return render_template('user/profile.html')
