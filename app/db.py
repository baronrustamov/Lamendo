import os
import sqlite3
from typing import NamedTuple

from flask import current_app, g

from .config import DATABASE, INIT_DATA, SCHEMA


# Dot notation > dictionary syntax for Jinja templates
class Board(NamedTuple):
    board_id: int
    board_acronym: str
    board_description: str


class Post(NamedTuple):
    post_id: int
    post_board_id: int
    user: str
    date: str
    post: str
    img_filename: str
    img_uniqid: str
    img_ext: str


class Reply(NamedTuple):
    reply_id: int
    reply_post_id: int
    user: str
    date: str
    reply: str
    img_filename: str
    img_uniqid: str
    img_ext: str


def init_db():
    """https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#initial-schemas"""
    with current_app.app_context():
        db = get_db()
        inits = [SCHEMA, INIT_DATA]
        for init in inits:
            with current_app.open_resource(init, mode='r') as f:
                sql_string = f.read()
                db.cursor().executescript(sql_string)
            db.commit()


def is_db_initialized():
    return os.path.exists(DATABASE)


def get_db():
    """https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#using-sqlite-3-with-flask
    https://www.reddit.com/r/flask/comments/5ggh7j/what_is_flaskg/
    """
    with current_app.app_context():
        db = getattr(g, 'database', None)
        if db is None:
            db_initialized = is_db_initialized()

            g.database = sqlite3.connect(DATABASE)

            if not db_initialized:
                init_db()

            db = g.database
        # Make using dictionary sytanx available with:
        db.row_factory = sqlite3.Row
        return db


def query_db(query, args=(), one=False):
    """https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#easy-querying"""
    with current_app.app_context():
        try:
            cur = get_db().execute(query, args)
            rv = cur.fetchall()
            cur.close()
            if rv == []:
                return None
            if one:
                return rv[0] if rv else None
            return rv
        except Exception as e:
            raise Exception(e) from None
