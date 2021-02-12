import logging
import os
from datetime import datetime
from functools import wraps

import pytz
from api import (
    create_feedback,
    create_post,
    create_reply,
    create_reply_to_reply,
    create_report,
    get_board_id,
    get_boards,
    get_boards_posts,
    get_post,
    get_popular_posts,
    get_post_replies,
    is_valid_ip,
)
from config import (
    FEEDBACK_MSG,
    IMG_PATH,
    LOG_PATH,
    MAX_FILE_SIZE,
    POST_MSG,
    REPLY_MSG,
    REPORT_MSG,
    RULES,
)
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from forms import FeedbackForm, PostCompiler, ReportForm
from urls import URLSpace
from utils import get_ip_from_request, upload_image

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


def validate_ip_for_post_request(redirect_to):
    """All functions accepting POST requests should use this
    to ensure banned IP addresses cannot submit forms to the site.
    Ban appeal forms are an exception.

    `redirect_to`: name of the function you want to route to
    if a bad IP is encountered.

    NOTE: using this will require the operand function to have an
    addition field for the ip address.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ip = get_ip_from_request(request)
            kwargs['ip'] = ip
            if request.method == 'POST':
                ip_status, msg = is_valid_ip(ip)
                if not ip_status:
                    flash(msg)
                    return redirect(url_for(redirect_to, **kwargs))
            return func(*args, **kwargs)

        return wrapper

    return decorator


@app.route('/', methods=['GET', 'POST'])
@validate_ip_for_post_request('home')
def home(ip):
    boards = get_boards()
    posts = get_popular_posts()
    feedback = FeedbackForm()

    if feedback.validate_on_submit():
        subject = feedback.subject.data
        message = feedback.message.data
        create_feedback(subject, message, ip)
        flash(FEEDBACK_MSG)
        return redirect(url_for('home'))

    return render_template(
        'home.html', boards=boards, posts=posts, feedback_form=feedback, rules=RULES
    )


@app.route('/<board_name>')
@URLSpace.validate_board
def board_catalog(board_name, boards):
    posts = get_boards_posts(board_name)
    report = ReportForm()
    return render_template(
        'catalog.html', board_name=board_name, boards=boards, posts=posts, report_form=report
    )


@app.route('/<board_name>/<post_id>')
@URLSpace.validate_board
def board_post(board_name, post_id, boards):
    post = get_post(post_id)
    if not post:
        abort(404)

    replies = get_post_replies(post_id)
    report = ReportForm()
    return render_template(
        'post.html',
        board_name=board_name,
        boards=boards,
        post=post,
        replies=replies,
        report_form=report,
    )


@app.route('/<board_name>/post', methods=['POST'])
@validate_ip_for_post_request('board_catalog')
@URLSpace.validate_board
def post_form(board_name, boards, ip):
    board_id = get_board_id(board_name)
    p = PostCompiler(request, 'form_text', 'form_img')

    if p.valid:
        if upload_image(p.img):
            create_post(board_id, p.text, p.img, p.user, ip)
            flash(POST_MSG)

    return redirect(url_for('board_catalog', board_name=board_name, boards=boards))


@app.route('/<board_name>/<post_id>/reply', methods=['POST'])
@validate_ip_for_post_request('board_post')
@URLSpace.validate_board
@URLSpace.validate_post
def reply_form(board_name, boards, post_id, ip):
    p = PostCompiler(request, 'form_text', 'form_img', require_img=False)

    if p.valid:
        upload_image(p.img)
        create_reply(post_id, p.text, p.img, p.user, ip)
        flash(REPLY_MSG)

    return redirect(url_for('board_post', board_name=board_name, boards=boards, post_id=post_id))


@app.route('/<board_name>/<post_id>/<reply_id>/reply', methods=['POST'])
@validate_ip_for_post_request('board_post')
@URLSpace.validate_board
@URLSpace.validate_post
@URLSpace.validate_reply
def reply_to_reply(board_name, boards, post_id, reply_id, ip):
    p = PostCompiler(request, 'form_text', 'form_img', require_img=False)

    if p.valid:
        upload_image(p.img)
        create_reply_to_reply(post_id, reply_id, p.text, p.img, p.user, ip)
        flash(REPLY_MSG)

    return redirect(url_for('board_post', board_name=board_name, boards=boards, post_id=post_id))


@app.route('/<board_name>/<post_id>/report', methods=['POST'])
@validate_ip_for_post_request('board_catalog')
@URLSpace.validate_board
@URLSpace.validate_post
def report_post(board_name, boards, post_id, ip):
    form = ReportForm()

    if form.validate_on_submit():
        category = form.category.data
        message = form.message.data
        create_report(post_id, None, category, message, ip)
        flash(REPORT_MSG)

    return redirect(url_for('board_catalog', board_name=board_name, boards=boards))


@app.route('/<board_name>/<post_id>/<reply_id>/report', methods=['POST'])
@validate_ip_for_post_request('board_post')
@URLSpace.validate_board
@URLSpace.validate_post
@URLSpace.validate_reply
def report_reply(board_name, boards, post_id, reply_id, ip):
    form = ReportForm()

    if form.validate_on_submit():
        category = form.category.data
        message = form.message.data
        create_report(post_id, reply_id, category, message, ip)
        flash(REPORT_MSG)

    return redirect(url_for('board_post', board_name=board_name, boards=boards, post_id=post_id))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
