import logging
import os
from datetime import datetime

from flask import Flask, abort, redirect, render_template, request, url_for
import pytz

from api import (
    create_post,
    create_reply,
    get_board_id,
    get_boards,
    get_boards_posts,
    get_post,
    get_post_replies,
)
from config import IMG_PATH, LOG_PATH
from urls import URLSpace
from utils import get_new_uniqid, upload_image

app = Flask(__name__)

app.secret_key = str(os.urandom(16))

app.config['UPLOAD_FOLDER'] = IMG_PATH
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 3_145_728

with app.app_context():
    app.url_space = URLSpace()

app.config['LOG_FILEPATH'] = LOG_PATH
logging.basicConfig(filename=app.config['LOG_FILEPATH'], level=logging.INFO)

logging.getLogger('werkzeug').setLevel(logging.ERROR)

eastern = pytz.timezone('US/Eastern')


@app.after_request
def after_request(response):
    env = request.environ
    attrs = [
        'REQUEST_URI',
        'REQUEST_METHOD',
        'REMOTE_ADDR',
        'REMOTE_PORT',
        'CONTENT_LENGTH',
        'HTTP_X_FORWARDED_FOR',
        'HTTP_REFERER',
    ]
    not_found = 'unknown'
    l = [f'{attr}: {env.get(attr, not_found)}' for attr in attrs]
    l.insert(0, eastern.fromutc(datetime.utcnow()).strftime('%c'))
    logging.info(', '.join(l))
    return response


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


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
    else:
        print('Replies require a body of text or an image.')

    return redirect(url_for('board_post', board_acronym=board_acronym, post_id=post_id))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
