import inspect
import os
import sqlite3

from flask import current_app, g

from .config import DATABASE, INIT_DATA, SCHEMA


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
            print('Query called from:', inspect.stack()[1][3])
            cur = get_db().execute(query, args)
            r = cur.fetchall()
            cur.close()
            if r == []:
                return None
            if one:
                return r[0] if r else None
            return r
        except Exception as e:
            raise Exception(e) from None
