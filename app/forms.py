import os
import re
from datetime import datetime
from time import time

from api import get_event, push_event
from config import (
    ALLOWED_FILETYPES,
    EVENT_COOLDOWN,
    IMG_PATH,
    LOG_PATH,
    MAX_FILE_SIZE,
    MAX_POST_LENGTH,
    MIN_POST_LENGTH,
    MAX_POST_ROWS,
    REPORTS,
)
from flask import current_app, flash
from utils import get_new_uid, get_username, make_img_from_request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, SelectField, validators


def valid_ip(ip):
    event = get_event(ip)
    msg = None
    if event and event.blacklisted:
        msg = 'IP address banned.'

    elif event and (time() - EVENT_COOLDOWN < event.last_event_date):
        msg = 'Wait 15 seconds between posts.'

    result = (True, msg) if msg is None else (False, msg)
    push_event(ip)
    return result


class FeedbackForm(FlaskForm):
    subject = StringField(
        'Subject', [validators.Length(min=1, max=64), validators.InputRequired()]
    )
    message = TextAreaField(
        'Message',
        [
            validators.Length(min=MIN_POST_LENGTH, max=MAX_POST_LENGTH),
            validators.InputRequired(),
        ],
    )


class ReportForm(FlaskForm):
    category = SelectField('Category', choices=[(r, r) for r in REPORTS])
    message = TextAreaField('Report', [validators.Length(max=MAX_POST_LENGTH),],)


class PostCompiler:
    def __init__(
        self,
        request,
        form_text_name=None,
        form_img_name=None,
        require_text=True,
        validate_text=True,
        require_img=True,
    ):
        self.valid = True
        self.invalid_message = None

        self.request = request
        self.text_name = form_text_name
        self.img_name = form_img_name
        self.require_text = require_text
        self.require_img = require_img
        self.validate_text = validate_text

        self.ip = PostCompiler.get_ip_from_request(self.request)
        self.text = request.form.get(form_text_name, None)
        self.img = make_img_from_request(request, form_img_name)
        self.user = get_username()

        self.event = get_event(self.ip)
        push_event(self.ip, event=self.event)

        self.set_is_valid()

    @staticmethod
    def get_ip_from_request(request):
        return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    def is_invalid_text(self):
        text_len = len(re.sub(r'\s', '', self.text))
        if text_len < MIN_POST_LENGTH or text_len > MAX_POST_LENGTH:
            return f'Min characters ({MIN_POST_LENGTH}). Max characters ({MAX_POST_LENGTH}).'

        text_row_count = self.text.count('\n')
        if text_row_count > MAX_POST_ROWS:
            return f'Max rows ({MAX_POST_ROWS})'

        return False

    def set_is_valid(self):
        assert self.invalid_message == None
        if self.event and self.event.blacklisted:
            self.invalid_message = 'IP address banned.'

        elif self.event and (time() - EVENT_COOLDOWN < self.event.last_event_date):
            self.invalid_message = 'Wait 15 seconds between posts.'

        elif self.require_img:
            if not self.img:
                self.invalid_message = 'No image submitted.'

        elif self.require_text:
            if not self.text:
                self.invalid_message = 'No text submitted.'
            elif self.validate_text:
                self.invalid_message = self.is_invalid_text()

        if self.invalid_message:
            self.valid = False
