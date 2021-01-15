import random
from datetime import datetime
from time import time
from typing import NamedTuple

from db import get_db, query_db
from utils import get_file_ext, get_filename_uid_from_img, make_date, make_none


# Dot notation > dictionary syntax for Jinja templates
class Board(NamedTuple):
    board_id: int
    board_acronym: str
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


class Reply(NamedTuple):
    reply_id: int
    reply_post_id: int
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
                r['reply_id'],
                r['reply_post_id'],
                r['user'],
                '' if r['reply'] is None else r['reply'],
                r['img_filename'],
                r['img_uid'],
                get_file_ext(r['img_filename']),
                make_date(r['date']),
            )
            replies.append(_r)
    return replies


def get_board_acronyms():
    sql_string = """
        select board_acronym
        from board;
    """
    rows = query_db(sql_string)
    return set(row['board_acronym'] for row in rows)


def get_post(post_id):
    sql_string = """
        select post.*
        from post
        where post.post_id = ?;
    """
    row = query_db(sql_string, args=[post_id], one=True)
    return make_post(row)


def get_post_replies(post_id):
    sql_string = """
        select reply.*
        from reply
        where reply.reply_post_id = ?;
    """
    rows = query_db(sql_string, args=[post_id])
    return make_replies(rows)


def get_boards_posts(board_acronym):
    sql_string = """
        select post.*
        from board
            left join post on board.board_id = post.post_board_id
        where board_acronym = ?
        and post.post_id is not null
        order by post_id;
    """
    rows = query_db(sql_string, args=[board_acronym])
    return make_posts(rows)


def get_boards():
    sql_string = 'select * from board;'
    row = query_db(sql_string)
    boards = ([Board(*board) for board in row]) if row else None
    return boards


def get_board_id(board_acronym):
    sql_string = 'select board_id from board where board_acronym = ?'
    row = query_db(sql_string, args=[board_acronym], one=True)
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


def create_post(post_board_id, text, img, user):
    sql_string = """insert into post(post_board_id, user, date, post, img_filename, img_uid)
                        values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""
    
    filename, uid = get_filename_uid_from_img(img)
    text = make_none(text)
    params = [post_board_id, user, text, filename, uid]
    query_db(sql_string, params)


def create_reply(reply_post_id, text, img, user):
    sql_string = """insert into reply(reply_post_id, user, date, reply, img_filename, img_uid)
                        values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""

    filename, uid = get_filename_uid_from_img(img)
    text = make_none(text)
    params = [reply_post_id, user, text, filename, uid]
    query_db(sql_string, params)


def create_report(post_id, reply_id, text):
    sql_string = """insert into report(post_id, reply_id, reason)
                    values (?, ?, ?);"""
    text = make_none(text)
    params = [post_id, reply_id, text]
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
