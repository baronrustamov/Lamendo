import random
from datetime import datetime
from functools import wraps
from pprint import pprint
from time import time
from typing import List, NamedTuple

from config import BANNED_MSG, COOLDOWN_MSG, EVENT_COOLDOWN, PRODUCTION
from db import get_db, query_db
from utils import get_file_ext, get_filename_uid_from_img, make_date, make_none


# NamedTuples because dot notation > dictionary syntax for Jinja templates
class Board(NamedTuple):
    board_id: int
    board_name: str
    board_description: str


class Post(NamedTuple):
    post_id: int
    post_board_id: int
    user: str
    post: str
    img_filename: str
    img_uid: str
    img_ext: str
    date: datetime
    post_board_name: str
    reply_count: int


class Reply(NamedTuple):
    reply_id: int
    reply_post_id: int
    parent_reply_id: int
    parent_user: List
    children: List
    user: str
    reply: str
    img_filename: str
    img_uid: str
    img_ext: str
    date: datetime


class Event(NamedTuple):
    event_id: int
    ip: str
    last_event_date: int
    blacklisted: bool
    blacklisted_until: int


def make_event(row):
    assert isinstance(row['blacklisted'], int)
    event = Event(
        row['event_id'],
        row['ip'],
        row['last_event_date'],
        True if row['blacklisted'] == 1 else False,
        row['blacklisted_until'],
    )
    return event


def make_post(row):
    if row:
        p = Post(
            row['post_id'],
            row['post_board_id'],
            row['user'],
            row['post'],
            row['img_filename'],
            row['img_uid'],
            get_file_ext(row['img_filename']),
            make_date(row['date']),
            row['post_board_name'],
            row['reply_count']
        )
        return p
    return None


def make_posts(rows):
    posts = ([make_post(p) for p in rows]) if rows else None
    return posts


def make_replies(rows):
    replies = None
    if rows:
        replies = []
        for r in rows:
            _r = Reply(
                int(r['reply_id']),
                int(r['reply_post_id']),
                None if not r['parent_reply_id'] else int(r['parent_reply_id']),
                [],
                [],
                r['user'],
                '' if r['reply'] is None else r['reply'],
                r['img_filename'],
                r['img_uid'],
                get_file_ext(r['img_filename']),
                make_date(r['date']),
            )
            replies.append(_r)
    return replies


def get_board_names():
    sql_string = """
        select board_name
        from board;
    """
    rows = query_db(sql_string)
    return set(row['board_name'] for row in rows) if rows else None


def get_post(post_id):
    sql_string = """
        select
            post.*,
            board.board_name post_board_name,
            count(*) reply_count
        from
            post
            left join reply on reply.reply_post_id = post.post_id
            left join board on board.board_id = post.post_board_id
        where post.post_id = ?
        group by
            post_id;
    """
    row = query_db(sql_string, args=[post_id], one=True)
    return make_post(row)


def get_popular_posts(n=4):
    sql_string = """
        select
            reply_post_id,
            count(*) reply_count
        from
            reply
        group by
            reply_post_id
        order by reply_count desc
        limit ?;
    """
    rows = query_db(sql_string, args=[n])
    if not rows:
        return None

    posts = []
    for r in rows:
        posts.append(get_post(r['reply_post_id']))
    return posts


def get_post_replies(post_id):
    sql_string = """
        select reply.*
        from reply
        where reply.reply_post_id = ?
        order by reply_id;
    """
    rows = query_db(sql_string, args=[post_id])
    if not rows:
        return None

    replies = make_replies(rows)
    replies = {reply.reply_id: reply for reply in replies}

    parent_user_index = 3
    children_index = 4
    user_index = 5
    for reply in replies.values():
        if reply.parent_reply_id is not None:
            replies[reply.parent_reply_id][children_index].append(reply.user)
            replies[reply.reply_id][parent_user_index].append(
                replies[reply.parent_reply_id][user_index]
            )

    return replies.values()


def get_boards_posts(board_name):
    sql_string = """
        select
            post.*,
            board_name post_board_name,
            count(*) reply_count
        from board
            left join post on board.board_id = post.post_board_id
            left join reply on reply.reply_post_id = post.post_id
        where board_name = ?
            and post.post_id is not null
        group by
            post_id
        order by post_id;
    """
    rows = query_db(sql_string, args=[board_name])
    return make_posts(rows)


def get_boards():
    sql_string = 'select * from board;'
    rows = query_db(sql_string)
    boards = ([Board(*board) for board in rows]) if rows else None
    return boards


def get_board_id(board_name):
    sql_string = 'select board_id from board where board_name = ?'
    row = query_db(sql_string, args=[board_name], one=True)
    board_id = row['board_id'] if row else None
    return board_id


def get_post_id(post_id):
    sql_string = 'select post_id from post where post_id = ?'
    row = query_db(sql_string, args=[post_id], one=True)
    post_id = row['post_id'] if row else None
    return post_id


def get_reply_id(reply_id):
    sql_string = 'select reply_id from reply where reply_id = ?'
    row = query_db(sql_string, args=[reply_id], one=True)
    reply_id = row['reply_id'] if row else None
    return reply_id


def event_wrapper(create_func):
    @wraps(create_func)
    def wrapper(*args, **kwargs):
        if PRODUCTION:
            push_event(args[-1])
        return create_func(*args, **kwargs)

    return wrapper


@event_wrapper
def create_board(board_name, board_description, ip):
    sql_string = """insert into board(board_name, board_description)
                                values (?, ?);"""
    params = [board_name, board_description]
    query_db(sql_string, params)


@event_wrapper
def create_post(post_board_id, text, img, user, ip):
    sql_string = """insert into post(post_board_id, user, date, post, img_filename, img_uid, ip)
                        values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?, ?);"""

    filename, uid = get_filename_uid_from_img(img)
    text = make_none(text)
    params = [post_board_id, user, text, filename, uid, ip]
    query_db(sql_string, params)


@event_wrapper
def create_reply(post_id, text, img, user, ip):
    sql_string = """insert into reply(reply_post_id, user, date, reply, img_filename, img_uid, ip)
                        values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?, ?);"""

    filename, uid = get_filename_uid_from_img(img)
    text = make_none(text)
    params = [post_id, user, text, filename, uid, ip]
    query_db(sql_string, params)


@event_wrapper
def create_reply_to_reply(post_id, parent_reply_id, text, img, user, ip):
    """
    Replies and replies to replies go in the same SQLite table.

        reply_id   parent_reply_id     text
        1          null                drawing is fun!
        2          1                   what did you draw?
        3          2                   a pink elephant.
        4          1                   drawing takes too much patience.
    """
    sql_string = """insert into reply(reply_post_id, parent_reply_id, user, date, reply, img_filename, img_uid, ip)
                        values (?, ?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?, ?);"""
    filename, uid = get_filename_uid_from_img(img)
    text = make_none(text)
    params = [post_id, parent_reply_id, user, text, filename, uid, ip]
    query_db(sql_string, params)


@event_wrapper
def create_report(post_id, reply_id, category, message, ip):
    sql_string = """insert into report(post_id, reply_id, category, message, ip)
                    values (?, ?, ?, ?, ?);"""
    message = make_none(message)
    params = [post_id, reply_id, category, message, ip]
    query_db(sql_string, params)


@event_wrapper
def create_feedback(subject, message, ip):
    sql_string = """insert into feedback(subject, message, ip)
                    values (?, ?, ?);"""
    subject, message = make_none(subject, message)
    params = [subject, message, ip]
    query_db(sql_string, params)


def get_event(ip):
    sql_string = """select * from event where ip = ?;"""
    row = query_db(sql_string, [ip], one=True)
    event = make_event(row) if row else None
    return event


def push_event(ip, event=None):
    if event == None:
        event = get_event(ip)

    if event:
        assert ip == event.ip
        sql_string = """update event
            set last_event_date = ?
            where ip = ?;"""
        query_db(sql_string, [time(), ip])
    else:
        sql_string = """insert into event(ip) values (?);"""
        query_db(sql_string, [ip], one=True)


def is_valid_ip(ip):
    event = get_event(ip)
    msg = None
    if event and event.blacklisted:
        msg = BANNED_MSG

    elif event and (time() - EVENT_COOLDOWN < event.last_event_date):
        msg = COOLDOWN_MSG

    result = (True, msg) if msg is None else (False, msg)
    return result
