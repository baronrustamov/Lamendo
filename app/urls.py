from functools import wraps

from api import get_boards, get_post_id, get_reply_id
from flask import abort, current_app


class URLSpace:
    def __init__(self):
        self.boards = get_boards()
        self.board_names = [b.board_name for b in self.boards] if self.boards else None

    def valid_board_name(self, val):
        return val in self.board_names

    @staticmethod
    def validate_board(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            board_name = kwargs['board_name']
            with current_app.app_context():
                kwargs['boards'] = current_app.url_space.boards
                if not current_app.url_space.valid_board_name(board_name):
                    abort(404)
            return fn(*args, **kwargs)

        return wrapper

    @staticmethod
    def validate_post(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            post_id = kwargs['post_id']
            with current_app.app_context():
                if not get_post_id(post_id):
                    abort(404)
            return fn(*args, **kwargs)

        return wrapper

    @staticmethod
    def validate_reply(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            reply_id = kwargs['reply_id']
            with current_app.app_context():
                if not get_reply_id(reply_id):
                    abort(404)
            return fn(*args, **kwargs)

        return wrapper
