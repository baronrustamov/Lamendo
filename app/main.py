import os

from flask import Flask, abort, redirect, render_template, request, url_for

from api import (
    create_post,
    create_reply,
    get_boards,
    get_boards_posts,
    get_post,
    get_post_replies,
    get_board_id
)
from db import query_db
from urls import URLSpace
from utils import get_new_uniqid, upload_image
from configs import IMG_PATH

app = Flask(__name__)
app.secret_key = str(os.urandom(16))

app.config['UPLOAD_FOLDER'] = IMG_PATH

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    app.url_space = URLSpace()


@app.route('/')
def home():
    boards = get_boards()
    return render_template('home.html', boards=boards)


@app.route('/<board_acronym>')
@URLSpace.validate_board
def board_catalog(board_acronym):
    posts = get_boards_posts(board_acronym)
    return render_template('board.html', board_acronym=board_acronym, posts=posts)


@app.route('/<board_acronym>/<post_id>')
@URLSpace.validate_board
def board_post(board_acronym, post_id):
    post = get_post(post_id)
    if not post:
        abort(404)

    replies = get_post_replies(post_id)

    return render_template(
        'post.html', board_acronym=board_acronym, post=post, replies=replies
    )


@app.route('/<board_acronym>/post', methods=['POST'])
@URLSpace.validate_board
def post_form(board_acronym):
    board_id = get_board_id(board_acronym)
    post = request.form.get('post_upload_text')

    img_uniqid = get_new_uniqid()
    img_obj = request.files.get('post_upload_img', None)

    if post and img_obj:
        upload_image(img_obj, img_uniqid)
        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        create_post(board_id, post, img_obj.filename, img_uniqid, ip)
        print(request.environ, request.remote_addr)
        print_upload_task('post', img_obj.filename)
    else:
        print('Posts require a body of text and an image.')

    return redirect(url_for('board_catalog', board_acronym=board_acronym))


@app.route('/<board_acronym>/<post_id>/reply', methods=['POST'])
@URLSpace.validate_board
def reply_form(board_acronym, post_id):
    reply = request.form.get('reply_upload_text')

    img_uniqid = get_new_uniqid()
    img_obj = request.files.get('reply_upload_img', None)

    if reply or img_obj:
        upload_image(img_obj, img_uniqid)
        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        create_reply(post_id, reply, img_obj.filename, img_uniqid, ip)
        print(request.environ, request.remote_addr)
        print_upload_task('reply', img_obj.filename)
    else:
        print('Replies require a body of text or an image.')

    return redirect(url_for('board_post', board_acronym=board_acronym, post_id=post_id))


def print_upload_task(text, filename):
    print(f'Received upload -- Text: {text} -- File: {filename}')

if __name__ == '__main__':
    app.run(host='0.0.0.0')