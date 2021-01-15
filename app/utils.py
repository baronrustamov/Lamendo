import os
import re
from datetime import datetime
from time import time

from config import (
    ALLOWED_FILETYPES,
    EVENT_COOLDOWN,
    IMG_PATH,
    LOG_PATH,
    MAX_FILE_SIZE,
    MAX_POST_LENGTH,
    MIN_POST_LENGTH,
)
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def make_none(*args):
    if args is None:
        return args

    l = []
    for arg in args:
        if arg == '':
            l.append(None)
        else:
            l.append(arg)
    if len(args) == 1:
        return l[0]
    return tuple(l)


def get_new_uid():
    # e.g. 0x385a482f97b356[2:]
    uid = hex(int(time() * 10_000_000))[2:]
    return uid


def get_file_ext(filename):
    if filename:
        ext = filename.split('.')[-1].lower()
        if (ext not in ALLOWED_FILETYPES) or (not isinstance(ext, str)):
            msg = str(ext) + ' not in ' + str(ALLOWED_FILETYPES)
            raise ValueError(msg)
        return ext
    return filename


def upload_image(img: FileStorage):
    """https://www.reddit.com/r/learnprogramming/comments/gamhq/generating_a_short_unique_id_in_python_similar_to/"""
    if img and is_file_allowed(img.filename):
        # >>> secure_filename('file!@#$%^&*.123_name1234..png')
        # 'file.123_name1234..png'
        filename = secure_filename(img.filename)
        # .png
        extension = get_file_ext(filename)
        # 385a482f97b356.png
        img_stored_filename = img.uid + '.' + extension
        # path/385a482f97b356.png
        with current_app.app_context():
            img_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], img_stored_filename
            )
        img.save(img_path)
        return True
    return False


def is_file_allowed(filename):
    # <something> then .png, .jpg, or .jpeg
    exts = '|'.join(ALLOWED_FILETYPES)
    match = bool(re.match(r'^.+(' + exts + ')$', filename))
    return match


def make_date(val):
    d = datetime.fromisoformat(val)
    return d.strftime('%B %d, %Y %H:%M')


def get_username():
    return get_new_uid()


def make_img_from_request(request, name) -> FileStorage:
    img = request.files.get(name, None)
    if not img:
        return None
    if not is_file_allowed(img.content_type.lower()):
        return None
    if img:
        img.uid = get_new_uid()
    return img


def get_filename_uid_from_img(img):
    filename, uid = None, None
    if img:
        filename = make_none(img.filename)
        uid = img.uid
    return filename, uid
