import datetime
import os
import random
import sqlite3
from typing import NamedTuple

from flask import Flask, g, render_template, request
from werkzeug.utils import secure_filename


DATABASE = 'db/img_board.db'
SCHEMA = 'db/schema.sql'
UPLOAD_FOLDER = 'static/uploads'
IMG_EXTS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Dot notation > dictionary syntax for use in our HTML
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
    image_file: str

class Reply(NamedTuple):
    reply_id: int
    reply_post_id: int
    user: str
    date: str
    post: str
    image_file: str


@app.route('/')
def home():
    sql_string = 'select * from board'
    boards = query_db(sql_string)
    board_NTs = [Board(board[0], board[1], board[2]) for board in boards]
    return render_template('home.html', boards=board_NTs)


@app.route('/<board_acronym>')
def board(board_acronym):
    sql_string = 'select post.* from board, post where board_acronym=? and post_board_id=board_id'
    posts = query_db(sql_string, args=[board_acronym])
    if posts:
        post_NTs = [Post(post[0], post[1], post[2], post[3], post[4], post[5]) for post in posts]
        return render_template('board.html', board_acronym=board_acronym, posts=post_NTs)
    else:
        return home()


@app.route('/<board_acronym>/post', methods=['POST'])
def post(board_acronym):
    sql_string = 'select board_id from board, post where board_acronym=? and post_board_id=board_id'
    board_id = query_db(sql_string, args=[board_acronym], one=True)[0]
    image_file = 'test_img1'
    if not board_id or type(board_id)!=int:
        print(f'board_id: {board_id}')
        raise ValueError
    post_rows = create_post(board_id, request.form.get('post_text'), image_file)
    print(f'Post upload successfull. {post_rows} rows.')
    return board(board_acronym)


def create_post(post_board_id, post, image_file):
    try:
        user = 'anon' + str(random.randint(10_000, 99_999))
        sql_string = """insert into post(post_board_id, user, date, post, image_file)
                            values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?);"""
        db = get_db()
        cur = db.cursor()
        cur.execute(sql_string, [post_board_id, user, post, image_file])
        db.commit()
        cur.close()
        return cur.lastrowid
    except Exception as e:
        raise ValueError(e)


def init_db():
    """https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#initial-schemas
    """
    with app.app_context():
        db = get_db()
        with app.open_resource(SCHEMA, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#using-sqlite-3-with-flask
    https://www.reddit.com/r/flask/comments/5ggh7j/what_is_flaskg/
    """
    db = getattr(g, '_database', None)
    if db is None:
        g._database = sqlite3.connect(DATABASE)
        db = g._database
    # Make using dictionary sytanx available with:
    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    """https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#easy-querying
    """
    try:
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        if one:
            return rv[0] if rv else None
        else:
            return rv
    except Exception as e:
        print(e)
