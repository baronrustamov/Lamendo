import os
import re
from datetime import datetime
from time import time

from flask import current_app
from werkzeug.utils import secure_filename

from config import ALLOWED_FILETYPES


def make_none(*args):
    l = []
    for arg in args:
        if arg == '':
            l.append(None)
        else:
            l.append(arg)
    return tuple(l)

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


def upload_image(img_obj, img_uniqid):
    """https://www.reddit.com/r/learnprogramming/comments/gamhq/generating_a_short_unique_id_in_python_similar_to/"""
    if img_obj and is_file_allowed(img_obj.filename):
        # >>> secure_filename('file!@#$%^&*.123_name1234..png')
        # 'file.123_name1234..png'
        filename = secure_filename(img_obj.filename)
        # .png
        extension = get_file_ext(filename)
        # 385a482f97b356.png
        img_stored_filename = img_uniqid + extension
        # path/385a482f97b356.png
        with current_app.app_context():
            img_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], img_stored_filename
            )
        img_obj.save(img_path)
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
