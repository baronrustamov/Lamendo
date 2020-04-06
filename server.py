import datetime
import os
import random
import re
import sqlite3
from typing import NamedTuple
from time import time

from flask import Flask, g, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename


app = Flask(__name__, static_url_path='/static')

UPLOAD_FOLDER = 'UPLOAD_FOLDER'
app.config[UPLOAD_FOLDER] = 'static/img_uploads'

DATABASE = 'db/img_board.db'
SCHEMA = 'db/schema.sql'


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
    image_filename: str
    image_uniqid: str
    image_ext: str

class Reply(NamedTuple):
    reply_id: int
    reply_post_id: int
    user: str
    date: str
    reply: str
    image_filename: str
    image_uniqid: str
    image_ext: str


@app.route('/')
def home():
    sql_string = 'select * from board'
    boards = query_db(sql_string)
    board_NTs = [Board(*board) for board in boards]
    return render_template('home.html', boards=board_NTs)


@app.route('/<board_acronym>')
def board(board_acronym):
    sql_string = 'select post.* from board, post where board_acronym=? and post_board_id=board_id'
    posts = query_db(sql_string, args=[board_acronym])
    # if posts:
    post_NTs = []
    for post in posts:
        # Want to make use of argument unpacking, Post(*post_cpy)
        # Need to unlock the tuple to change some args
        post_cpy = list(post)
        post_cpy[6] = str(post[6])
        post_cpy.append(get_file_ext(post[5]))
        nt = Post(*post_cpy)
        post_NTs.append(nt)
    return render_template('board.html', board_acronym=board_acronym, posts=post_NTs)
    # else:
    #     return redirect(url_for('home'))


@app.route('/<board_acronym>/post', methods=['POST'])
def post(board_acronym):
    sql_string = 'select board_id from board, post where board_acronym=? and post_board_id=board_id'
    try:
        board_id = query_db(sql_string, args=[board_acronym], one=True)[0]
    except:
        enum = {'g': 1, 'ck': 2, 'b': 3}
        board_id = enum[board_acronym]

    post = request.form.get('post_upload_text')
    
    image_uniqid = None
    image_obj = request.files['post_upload_image']
    image_obj.filename = image_obj.filename.lower()
    if image_obj.filename != '':
        image_uniqid = get_new_uniqid()
        upload_successful = upload_img(image_obj, image_uniqid)
        if not upload_successful:
            print('Upload unsuccessful.')
            return redirect(url_for('board', board_acronym=board_acronym))

    if not board_id or type(board_id)!=int:
        raise ValueError(f'board_id: {board_id}')

    # Important check since we do not enforce NOT NULL in the db schema
    if post or image_obj.filename:
        create_post(board_id, post, image_obj.filename, image_uniqid)
    
    print_upload_task(post, image_obj.filename)

    return redirect(url_for('board', board_acronym=board_acronym))



def print_upload_task(post, filename):
    msg = 'Uploaded: '
    if post:
        msg+='post'
    if filename:
        msg+='image'
    if not post and not filename:
        msg+='nothing'
    msg+='.'
    print(msg)


def create_post(post_board_id, post, image_filename, image_uniqid):
    try:
        user = 'anon' + str(random.randint(10_000, 99_999))
        sql_string = """insert into post(post_board_id, user, date, post, image_filename, image_uniqid)
                            values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""
        db = get_db()
        cur = db.cursor()
        if image_filename == '': image_filename = None
        if post == '': post = None
        cur.execute(sql_string, [post_board_id, user, post, image_filename, image_uniqid])
        db.commit()
        cur.close()
        return cur.lastrowid
    except Exception as e:
        raise ValueError(e)


def get_new_uniqid():
    # e.g. 0x385a482f97b356[2:]
    image_uniqid = hex(int(time()*10_000_000))[2:]
    return image_uniqid


def get_file_ext(filename):
    if filename:
        return '.' + filename.split('.')[-1].lower()
    else:
        return str(filename)


def upload_img(image_obj, image_uniqid):
    """https://www.reddit.com/r/learnprogramming/comments/gamhq/generating_a_short_unique_id_in_python_similar_to/
    """
    if image_obj and file_allowed(image_obj.filename):
        # >>> secure_filename('file!@#$%^&*.123_name1234..png')
        # 'file.123_name1234..png'
        filename = secure_filename(image_obj.filename)
        # .png
        extension = get_file_ext(filename)
        # 385a482f97b356.png
        image_stored_filename = image_uniqid + extension
        # db/img_uploads/385a482f97b356.png
        image_path = os.path.join(app.config[UPLOAD_FOLDER], image_stored_filename)
        image_obj.save(image_path)
        return True
    else:
        return False


def file_allowed(filename):
    # <something> then .png, .jpg, or .jpeg
    match = bool(re.match(r'^.+\.(png|jpg|jpeg|gif)$', filename))
    return match


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
