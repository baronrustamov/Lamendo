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
    MAX_POST_ROWS
)
from flask import current_app
from utils import get_new_uid, get_username, make_img_from_request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


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

        self.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        self.text = request.form.get(form_text_name, None)
        self.img = make_img_from_request(request, form_img_name)
        self.user = get_username()

        self.event = get_event(self.ip)
        push_event(self.ip, event=self.event)

        self.set_is_valid()

    def is_invalid_text(self):
        text_len = len(self.text)
        if text_len < MIN_POST_LENGTH or text_len > MAX_POST_LENGTH:
            return f'Text must be between {MIN_POST_LENGTH} and {MAX_POST_LENGTH} characters.'

        text_row_count = self.text.count('\n')
        if text_row_count > MAX_POST_ROWS:
            return f'Text must have fewer than {MAX_POST_ROWS} rows.'

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
