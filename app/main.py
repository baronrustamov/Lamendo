import logging
import os
from datetime import datetime, timedelta
from functools import wraps

from api import (
    create_feedback,
    create_post,
    create_reply,
    create_reply_to_reply,
    create_report,
    get_board_id,
    get_boards,
    get_boards_posts,
    get_feedbacks,
    get_popular_posts,
    get_post,
    get_post_replies,
    get_posts,
    get_replies,
    get_reports,
    get_user,
    is_valid_ip,
)
from config import (
    FEEDBACK_MSG,
    IMG_PATH,
    LOG_PATH,
    MAX_FILE_SIZE,
    POST_MSG,
    PRODUCTION,
    REPLY_MSG,
    REPORT_MSG,
    RULES,
)
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from forms import FeedbackForm, LoginForm, PostCompiler, ReportForm
from urls import URLSpace
from utils import get_ip_from_request, upload_image
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = str(os.urandom(32))

# from redis import Redis
# r = Redis(host='localhost', port=6379, db=0)
# app.config['SESSION_REDIS'] = r

app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=2)
sess = Session()
sess.init_app(app)

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

# @app.errorhandler(Exception)
# def all_exception_handler(error):
#    return 'Internal Server Error', 500


@app.after_request
def after_request(response):
    env = request.environ
    attrs = [
        'REQUEST_METHOD',
        'REMOTE_ADDR',
        'REQUEST_URI',
        'REMOTE_PORT',
        'CONTENT_LENGTH',
        'HTTP_X_FORWARDED_FOR',
        'HTTP_REFERER',
    ]
    not_found = 'unknown'
    l = [f'{attr}: {env.get(attr, not_found)}' for attr in attrs]
    l.insert(0, datetime.utcnow().strftime('%c'))
    logging.info('~ '.join(l))
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

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            ip = get_ip_from_request(request)
            kwargs['ip'] = ip
            if request.method == 'POST':
                ip_status, msg = is_valid_ip(ip)
                if not ip_status:
                    flash(msg)
                    d = {}
                    if 'board_name' in kwargs:
                        d['board_name'] = kwargs['board_name']
                    if 'post_id' in kwargs and redirect_to != 'board_catalog':
                        d['post_id'] = kwargs['post_id']
                    return redirect(url_for(redirect_to, **d))
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@app.route('/', methods=['GET', 'POST'])
@validate_ip_for_post_request('home')
def home(ip):
    boards = get_boards()
    posts = get_popular_posts()
    feedback = FeedbackForm()
    report = ReportForm()

    if feedback.validate_on_submit():
        subject = feedback.subject.data
        message = feedback.message.data
        create_feedback(subject, message, ip)
        flash(FEEDBACK_MSG)
        return redirect(url_for('home'))

    return render_template(
        'home.html',
        boards=boards,
        posts=posts,
        feedback_form=feedback,
        report_form=report,
        rules=RULES,
    )


def login_required(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return fn(*args, **kwargs)

    return decorated_function


@app.route('/moderate')
@login_required
def moderate():
    days = 2
    since = timedelta(days=days)

    boards = get_boards()
    posts = get_posts(since=since)
    replies = get_replies(since=since)
    reports = get_reports(since=since)
    feedbacks = get_feedbacks(since=since)
    return render_template(
        'moderate.html',
        boards=boards,
        posts=posts,
        replies=replies,
        reports=reports,
        feedbacks=feedbacks,
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    msg = 'Username or password incorrect.'
    if login_form.validate_on_submit():
        username = login_form.username.data
        password_candidate = login_form.password.data

        user_record = get_user(username)
        if user_record:
            if check_password_hash(user_record.password, password_candidate):
                session['logged_in'] = True
                session['username'] = username
                flash('Login successful.')
                return redirect(url_for('moderate'))
        flash(msg)
    return render_template('login.html', login_form=login_form)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logged out successful.')
    return redirect(url_for('home'))


@app.route('/<board_name>')
@URLSpace.validate_board
def board_catalog(board_name, boards):
    posts = get_boards_posts(board_name)
    report = ReportForm()
    return render_template(
        'catalog.html',
        board_name=board_name,
        boards=boards,
        posts=posts,
        report_form=report,
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

    return redirect(url_for('board_catalog', board_name=board_name))


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

    return redirect(url_for('board_post', board_name=board_name, post_id=post_id))


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

    return redirect(url_for('board_post', board_name=board_name, post_id=post_id))


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

    return redirect(url_for('board_catalog', board_name=board_name))


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

    return redirect(url_for('board_post', board_name=board_name, post_id=post_id))


if not PRODUCTION:
    if __name__ == '__main__':
        app.run(host='0.0.0.0')
