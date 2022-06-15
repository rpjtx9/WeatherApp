import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

# Need to decide which one of these two database connection functions to use, if any! Might just use sqlitealchemy?
# Function 1
def db_connection():
    db = sqlite3.connect('weather.db')
    db.row_factory = sqlite3.Row
    return db
# Function 2
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()