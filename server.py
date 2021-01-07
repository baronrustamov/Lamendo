import os
import random
import re
import sqlite3
from time import time
from typing import NamedTuple

from flask import Flask, g, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static')
app.secret_key = str(os.urandom(16))

UPLOAD_FOLDER = 'UPLOAD_FOLDER'
ALLOWED_FILETYPES = {'.png', '.jpg', '.jpeg', '.gif'}
app.config[UPLOAD_FOLDER] = os.path.join(
    os.path.dirname(__file__), 'static/img_uploads'
)
os.makedirs(app.config[UPLOAD_FOLDER], exist_ok=True)

DATABASE = 'db/img_board.db'
SCHEMA = 'db/schema.sql'
INIT_DATA = 'db/init_data.sql'


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


@app.route('/')
def home():
    sql_string = 'select * from board;'
    sql_row_obj = query_db(sql_string)
    boards = ([Board(*board) for board in sql_row_obj]) if sql_row_obj else None
    return render_template('home.html', boards=boards)


@app.route('/<board_acronym>')
def board_catalog(board_acronym):
    sql_string = """
        select post.*
        from board
            left join post on board.board_id = post.post_board_id
        where board_acronym = ?
        and post.post_id is not null
        order by post_id;
    """
    sql_row_objs = query_db(sql_string, args=[board_acronym])
    posts = ([Post(*p, get_file_ext(p[5])) for p in sql_row_objs]) if sql_row_objs else None

    return render_template('board.html', board_acronym=board_acronym, posts=posts)


@app.route('/<board_acronym>/<post_id>')
def board_post(board_acronym, post_id):
    sql_string = """
        select post.*
        from post
        where post.post_id = ?;
    """
    sql_row_objs = query_db(sql_string, args=[post_id])
    post = [Post(*p, get_file_ext(p[5])) for p in sql_row_objs][0]

    sql_string = """
        select reply.*
        from reply
        where reply.reply_post_id = ?;
    """
    sql_row_objs = query_db(sql_string, args=[post_id])
    if sql_row_objs:
        replies = [Reply(*r, get_file_ext(r[5])) for r in sql_row_objs]
    else:
        replies = None

    return render_template(
        'post.html', board_acronym=board_acronym, post=post, replies=replies
    )


@app.route('/<board_acronym>/post', methods=['POST'])
def post_form(board_acronym):
    sql_string = 'select board_id from board where board_acronym = ?'
    board_id = query_db(sql_string, args=[board_acronym], one=True)[0]

    post = request.form.get('post_upload_text')

    img_uniqid = None
    img_obj = request.files['post_upload_img']
    img_obj.filename = img_obj.filename.lower()
    if img_obj.filename != '':
        img_uniqid = get_new_uniqid()
        upload_successful = upload_img(img_obj, img_uniqid)
        if not upload_successful:
            print('Post upload unsuccessful.')
            return redirect(url_for('board', board_acronym=board_acronym))

    if not board_id or not isinstance(board_id, int):
        raise ValueError(f'board_id: {board_id}')

    # Important to check since we do not enforce NOT NULL in the db schema
    if post or img_obj.filename:
        create_post(board_id, post, img_obj.filename, img_uniqid)

        print_upload_task('post', img_obj.filename)

    return redirect(url_for('board_catalog', board_acronym=board_acronym))


@app.route('/<board_acronym>/<post_id>/reply', methods=['POST'])
def reply_form(board_acronym, post_id):
    print('rpekrpiwejg')
    reply = request.form.get('reply_upload_text')

    img_uniqid = None
    img_obj = request.files['reply_upload_img']
    img_obj.filename = img_obj.filename.lower()
    if img_obj.filename != '':
        img_uniqid = get_new_uniqid()
        upload_successful = upload_img(img_obj, img_uniqid)
        if not upload_successful:
            print('Reply upload unsuccessful.')
            return redirect(url_for('board', board_acronym=board_acronym))

    # Important to check since we do not enforce NOT NULL in the db schema
    if reply or img_obj.filename:
        create_reply(post_id, reply, img_obj.filename, img_uniqid)

        print_upload_task('reply', img_obj.filename)

    return redirect(url_for('board_post', board_acronym=board_acronym, post_id=post_id))


def print_upload_task(text, filename):
    print(f'Received upload -- Text: {text} -- File: {filename}')


def create_post(post_board_id, post, img_filename, img_uniqid):
    try:
        user = 'anon' + str(random.randint(10_000, 99_999))
        sql_string = """insert into post(post_board_id, user, date, post, img_filename, img_uniqid)
                            values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""
        db = get_db()
        cur = db.cursor()
        if img_filename == '':
            img_filename = None
        if post == '':
            post = None
        cur.execute(sql_string, [post_board_id, user, post, img_filename, img_uniqid])
        db.commit()
        cur.close()
        return cur.lastrowid
    except Exception as e:
        raise ValueError(e) from None


def create_reply(reply_post_id, reply, img_filename, img_uniqid):
    try:
        user = 'anon' + str(random.randint(10_000, 99_999))
        sql_string = """insert into reply(reply_post_id, user, date, reply, img_filename, img_uniqid)
                            values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""
        db = get_db()
        cur = db.cursor()
        if img_filename == '':
            img_filename = None
        if reply == '':
            reply = None
        cur.execute(sql_string, [reply_post_id, user, reply, img_filename, img_uniqid])
        db.commit()
        cur.close()
        return cur.lastrowid
    except Exception as e:
        raise ValueError(e) from None


def get_new_uniqid():
    # e.g. 0x385a482f97b356[2:]
    img_uniqid = hex(int(time() * 10_000_000))[2:]
    return img_uniqid


def get_file_ext(filename):
    if filename:
        ext = '.' + filename.split('.')[-1].lower()
        if (ext not in ALLOWED_FILETYPES) or (not isinstance(ext, str)):
            msg = str(ext) + ' not in ' + str(ALLOWED_FILETYPES)
            raise ValueError(msg)
        return ext
    return filename


def upload_img(img_obj, img_uniqid):
    """https://www.reddit.com/r/learnprogramming/comments/gamhq/generating_a_short_unique_id_in_python_similar_to/"""
    if img_obj and file_allowed(img_obj.filename):
        # >>> secure_filename('file!@#$%^&*.123_name1234..png')
        # 'file.123_name1234..png'
        filename = secure_filename(img_obj.filename)
        # .png
        extension = get_file_ext(filename)
        # 385a482f97b356.png
        img_stored_filename = img_uniqid + extension
        # path/385a482f97b356.png
        img_path = os.path.join(app.config[UPLOAD_FOLDER], img_stored_filename)
        img_obj.save(img_path)
        return True
    return False


def file_allowed(filename):
    # <something> then .png, .jpg, or .jpeg
    exts = '|'.join(ALLOWED_FILETYPES)
    match = bool(re.match(r'^.+(' + exts + ')$', filename))
    return match


def init_db():
    """https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#initial-schemas"""
    with app.app_context():
        db = get_db()
        inits = [SCHEMA, INIT_DATA]
        for init in inits:
            with app.open_resource(init, mode='r') as f:
                sql_string = f.read()
                db.cursor().executescript(sql_string)
            db.commit()


def is_db_initialized():
    return os.path.exists(DATABASE)


def get_db():
    """https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/#using-sqlite-3-with-flask
    https://www.reddit.com/r/flask/comments/5ggh7j/what_is_flaskg/
    """
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
