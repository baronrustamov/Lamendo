import os

from flask import Flask, abort, redirect, render_template, request, url_for

from .api import (
    create_post,
    create_reply,
    get_boards,
    get_boards_posts,
    get_post,
    get_post_replies,
)
from .db import query_db
from .urls import URLSpace
from .utils import get_new_uniqid, upload_image

app = Flask(__name__, static_url_path='/static')
app.secret_key = str(os.urandom(16))

app.config['UPLOAD_FOLDER'] = os.path.join(
    os.path.dirname(__file__), 'static/img_uploads'
)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    app.url_space = URLSpace()


@app.route('/')
def home():
    boards = get_boards()
    return render_template('home.html', boards=boards)


@app.route('/<board_acronym>')
def board_catalog(board_acronym):
    if not app.url_space.valid_board_acronym(board_acronym):
        abort(404)

    posts = get_boards_posts(board_acronym)

    return render_template('board.html', board_acronym=board_acronym, posts=posts)


@app.route('/<board_acronym>/<post_id>')
def board_post(board_acronym, post_id):
    if not app.url_space.valid_board_acronym(board_acronym):
        abort(404)

    post = get_post(post_id)
    if not post:
        abort(404)

    replies = get_post_replies(post_id)
    if not replies:
        abort(404)

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
        upload_successful = upload_image(img_obj, img_uniqid)
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
        upload_successful = upload_image(img_obj, img_uniqid)
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
