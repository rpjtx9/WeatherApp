from flask_sqlalchemy import SQLAlchemy

import click
from flask import current_app, g
from flask.cli import with_appcontext

# Need to decide which one of these two database connection functions to use, if any! Might just use sqlitealchemy?
# Function 1

def get_db():
    if 'db' not in g:
        g.db = SQLAlchemy(app)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()