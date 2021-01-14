import os
import re
from datetime import datetime
from time import time

from flask import current_app
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from config import ALLOWED_FILETYPES, IMG_PATH, LOG_PATH, MIN_POST_LENGTH, MAX_POST_LENGTH, MAX_FILE_SIZE, EVENT_COOLDOWN
from api import get_event, push_event

from utils import get_username, get_new_uid, make_img_from_request

class PostCompiler:
    def __init__(self, request, form_text_name, form_img_name, require_text=True, require_img=True):
        self.valid = True
        self.invalid_message = None

        self.request = request
        self.text_name = form_text_name
        self.img_name = form_img_name
        self.require_text = require_text
        self.require_img = require_img

        self.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

        self.text = request.form.get(form_text_name, None)

        self.img = make_img_from_request(request, form_img_name)

        self.user = get_username()

        self.event = get_event(self.ip)
        push_event(self.ip, event=self.event)

        self.set_is_valid()

    def is_valid_text(self):
        no_space_len = len(re.sub(r'\s', '', self.text))
        if no_space_len < MIN_POST_LENGTH or no_space_len > MAX_POST_LENGTH:
            return False
        return True
    
    def set_is_valid(self):
        assert self.invalid_message == None

        if self.event.blacklisted:
            self.invalid_message = 'IP address banned.'

        elif time() - EVENT_COOLDOWN < self.event.last_event_date:
            self.invalid_message = 'Wait 15 seconds between posts.'

        elif self.require_img and not self.img:
            self.invalid_message = 'No image submitted.'

        elif self.require_text and not self.text:
            self.invalid_message = 'No text submitted.'

        elif self.require_text and not self.is_valid_text():
            self.invalid_message = 'Text lacks quality.'

        if self.invalid_message:
            self.valid = False