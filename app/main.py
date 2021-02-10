import logging
import os
from datetime import datetime

import pytz
from api import (
    create_post,
    create_reply,
    create_reply_to_reply,
    create_report,
    create_feedback,
    get_board_id,
    get_boards,
    get_boards_posts,
    get_post,
    get_post_replies,
)
from config import IMG_PATH, LOG_PATH, MAX_FILE_SIZE, RULES
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from forms import PostCompiler, FeedbackForm, ReportForm
from urls import URLSpace
from utils import upload_image

app = Flask(__name__)
app.secret_key = str(os.urandom(16))


assert os.path.isdir(IMG_PATH)
app.config['UPLOAD_FOLDER'] = IMG_PATH


app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

with app.app_context():
    app.url_space = URLSpace()

app.config['LOG_FILEPATH'] = LOG_PATH
os.makedirs(os.path.dirname(app.config['LOG_FILEPATH']), exist_ok=True)
logging.basicConfig(filename=app.config['LOG_FILEPATH'], level=logging.INFO)

logging.getLogger('werkzeug').setLevel(logging.ERROR)

csrf = CSRFProtect(app)

eastern = pytz.timezone('US/Eastern')


# @app.errorhandler(Exception)
# def all_exception_handler(error):
#    return 'Internal Server Error', 500


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


@app.route('/', methods=['GET', 'POST'])
def home():
    boards = get_boards()
    form = FeedbackForm()
    if form.validate_on_submit():
        subject = form.subject.data
        message = form.message.data
        ip = PostCompiler.get_ip_from_request(request)
        create_feedback(subject, message, ip)
        msg = 'Thank you for your feedback!'
        flash(msg)
        return redirect(url_for('home'))
    return render_template('home.html', boards=boards, form=form, rules=RULES)


@app.route('/<board_name>')
@URLSpace.validate_board
def board_catalog(board_name):
    posts = get_boards_posts(board_name)
    report_form = ReportForm()
    return render_template(
        'catalog.html', board_name=board_name, posts=posts, report_form=report_form
    )


@app.route('/<board_name>/<post_id>')
@URLSpace.validate_board
def board_post(board_name, post_id):
    post = get_post(post_id)
    if not post:
        abort(404)

    replies = get_post_replies(post_id)
    report_form = ReportForm()
    return render_template(
        'post.html',
        board_name=board_name,
        post=post,
        replies=replies,
        report_form=report_form,
    )


@app.route('/<board_name>/post', methods=['POST'])
@URLSpace.validate_board
def post_form(board_name):
    board_id = get_board_id(board_name)
    p = PostCompiler(request, 'form_text', 'form_img')
    msg = 'Post submitted.'
    if p.valid:
        if upload_image(p.img):
            create_post(board_id, p.text, p.img, p.user, p.ip)
        else:
            msg = 'Trouble uploading image.'
    else:
        msg = p.invalid_message
    flash(msg)
    return redirect(url_for('board_catalog', board_name=board_name))


@app.route('/<board_name>/<post_id>/reply', methods=['POST'])
@URLSpace.validate_board
@URLSpace.validate_post
def reply_form(board_name, post_id):
    p = PostCompiler(request, 'form_text', 'form_img', require_img=False)
    msg = 'Reply submitted.'
    if p.valid:
        upload_image(p.img)
        create_reply(post_id, p.text, p.img, p.user, p.ip)
    else:
        msg = p.invalid_message
    flash(msg)
    return redirect(url_for('board_post', board_name=board_name, post_id=post_id))


@app.route('/<board_name>/<post_id>/report', methods=['POST'])
@URLSpace.validate_board
@URLSpace.validate_post
def report_post(board_name, post_id):
    form = ReportForm()
    if form.validate_on_submit():
        category = form.category.data
        message = form.message.data
        create_report(
            post_id, None, category, message, PostCompiler.get_ip_from_request(request)
        )
        flash('Report Submitted, Thank You.')

    return redirect(url_for('board_catalog', board_name=board_name))


@app.route('/<board_name>/<post_id>/<reply_id>/report', methods=['POST'])
@URLSpace.validate_board
@URLSpace.validate_post
@URLSpace.validate_reply
def report_reply(board_name, post_id, reply_id):
    p = PostCompiler(request, 'form_text', None, require_text=False, require_img=False)
    msg = 'Report Submitted, Thank You.'
    if p.valid:
        create_report(post_id, reply_id, 'report_reply', 'report_reply', p.ip)
    else:
        msg = p.invalid_message if p.invalid_message else 'Could not submit report.'
    flash(msg)
    return redirect(url_for('board_post', board_name=board_name, post_id=post_id))


@app.route('/<board_name>/<post_id>/<reply_id>/reply', methods=['POST'])
@URLSpace.validate_board
@URLSpace.validate_post
@URLSpace.validate_reply
def reply_to_reply(board_name, post_id, reply_id):
    p = PostCompiler(request, 'form_text', 'form_img', require_img=False)
    msg = 'Reply submitted.'
    if p.valid:
        upload_image(p.img)
        create_reply_to_reply(post_id, reply_id, p.text, p.img, p.user, p.ip)
    else:
        msg = p.invalid_message if p.invalid_message else 'Could not submit reply.'
    flash(msg)
    return redirect(url_for('board_post', board_name=board_name, post_id=post_id))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
