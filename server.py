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
ALLOWED_FILETYPES = {'.png', '.jpg', '.jpeg', '.gif'}
app.config[UPLOAD_FOLDER] = 'static/img_uploads'

DATABASE = 'db/img_board.db'
SCHEMA = 'db/schema.sql'


# Dot notation > dictionary syntax for use in JINJA
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
    # reply: 'Reply'

class Reply(NamedTuple):
    reply_id: int
    reply_post_id: int
    user: str
    date: str
    reply: str
    image_filename: str
    image_uniqid: str
    image_ext: str

class Post_Reply(NamedTuple):
    post: 'Post'
    reply: 'Reply'


@app.route('/')
def home():
    sql_string = 'select * from board'
    boards = query_db(sql_string)
    board_NTs = [Board(*board) for board in boards]
    return render_template('home.html', boards=board_NTs)


@app.route('/<board_acronym>')
def board(board_acronym):
    sql_string = """
                    select post.*, reply.*
                    from board
                        left join post on board.board_id = post.post_board_id
                        left join reply on post.post_id = reply.reply_post_id
                    where board_acronym=?;
                """
    posts = query_db(sql_string, args=[board_acronym])
    if posts[0][0]:
        # Create format: post = [post, replies]
        post_dict = {}
        for post in posts:
            post_id = post[0]
            if post_id not in post_dict.keys():
                post_cpy = list(post)[:7]
                post_cpy.append(get_file_ext(post_cpy[5]))
                post_dict[post_id] = {'post': Post(*post_cpy), 'reply': []}

            reply_args = list(post[7:])
            reply_args.append(get_file_ext(post[-2]))
            if any(reply_args):
                reply = Reply(*reply_args)
                post_dict[post_id]['reply'].append(reply)
            else:
                post_dict[post_id]['reply'] = None

        posts = []
        for post in post_dict.values():
            posts.append(Post_Reply(post['post'], post['reply']))
    else:
        posts = None

    return render_template('board.html', board_acronym=board_acronym, posts=posts)


@app.route('/<board_acronym>/post', methods=['POST'])
def post(board_acronym):
    sql_string = 'select board_id from board where board_acronym = ?'
    board_id = query_db(sql_string, args=[board_acronym], one=True)[0]
 
    post = request.form.get('post_upload_text')
    
    image_uniqid = None
    image_obj = request.files['post_upload_image']
    image_obj.filename = image_obj.filename.lower()
    if image_obj.filename != '':
        image_uniqid = get_new_uniqid()
        upload_successful = upload_img(image_obj, image_uniqid)
        if not upload_successful:
            print('Post upload unsuccessful.')
            return redirect(url_for('board', board_acronym=board_acronym))

    if not board_id or type(board_id)!=int:
        raise ValueError(f'board_id: {board_id}')

    # Important to check since we do not enforce NOT NULL in the db schema
    if post or image_obj.filename:
        create_post(board_id, post, image_obj.filename, image_uniqid)
    
    print_upload_task('post', image_obj.filename)

    return redirect(url_for('board', board_acronym=board_acronym))


@app.route('/<board_acronym>/<post_id>/reply', methods=['POST'])
def reply(board_acronym, post_id):
    reply = request.form.get('reply_upload_text')
    
    image_uniqid = None
    image_obj = request.files['reply_upload_image']
    image_obj.filename = image_obj.filename.lower()
    if image_obj.filename != '':
        image_uniqid = get_new_uniqid()
        upload_successful = upload_img(image_obj, image_uniqid)
        if not upload_successful:
            print('Reply upload unsuccessful.')
            return redirect(url_for('board', board_acronym=board_acronym))

    # Important to check since we do not enforce NOT NULL in the db schema
    if reply or image_obj.filename:
        create_reply(post_id, reply, image_obj.filename, image_uniqid)
    
    print_upload_task('reply', image_obj.filename)

    return redirect(url_for('board', board_acronym=board_acronym))


def print_upload_task(text, filename):
    msg = 'Uploaded: '
    if text:
        msg+=text
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


def create_reply(reply_post_id, reply, image_filename, image_uniqid):
    try:
        user = 'anon' + str(random.randint(10_000, 99_999))
        sql_string = """insert into reply(reply_post_id, user, date, reply, image_filename, image_uniqid)
                            values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""
        db = get_db()
        cur = db.cursor()
        if image_filename == '': image_filename = None
        if reply == '': reply = None
        cur.execute(sql_string, [reply_post_id, user, reply, image_filename, image_uniqid])
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
        ext = '.' + filename.split('.')[-1].lower()
        if (ext not in ALLOWED_FILETYPES) or (not isinstance(ext, str)):
            msg = str(ext) + ' not in ' + str(ALLOWED_FILETYPES)
            raise ValueError(msg)
        else:
            return ext
    else:
        return filename


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
    exts = '|'.join(ALLOWED_FILETYPES)
    match = bool(re.match(r'^.+(' + exts +')$', filename))
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
