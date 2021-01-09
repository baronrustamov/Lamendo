import random
from datetime import datetime
from typing import NamedTuple

from db import get_db, query_db
from utils import get_file_ext, make_date, make_none


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
    img_uniqid: str
    img_ext: str
    date: datetime


class Reply(NamedTuple):
    reply_id: int
    reply_post_id: int
    user: str
    reply: str
    img_filename: str
    img_uniqid: str
    img_ext: str
    date: datetime


def make_post(sql_row_obj):
    if sql_row_obj:
        p = Post(
            sql_row_obj['post_id'],
            sql_row_obj['post_board_id'],
            sql_row_obj['user'],
            sql_row_obj['post'],
            sql_row_obj['img_filename'],
            sql_row_obj['img_uniqid'],
            get_file_ext(sql_row_obj['img_filename']),
            make_date(sql_row_obj['date']),
        )
        return p
    return None


def make_posts(sql_row_objs):
    posts = ([make_post(p) for p in sql_row_objs]) if sql_row_objs else None
    return posts


def make_replies(sql_row_objs):
    replies = None
    if sql_row_objs:
        replies = []
        for r in sql_row_objs:
            _r = Reply(
                r['reply_id'],
                r['reply_post_id'],
                r['user'],
                '' if r['reply'] is None else r['reply'],
                r['img_filename'],
                r['img_uniqid'],
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
    sql_row_objs = query_db(sql_string)
    return set(row['board_acronym'] for row in sql_row_objs)


def get_post(post_id):
    sql_string = """
        select post.*
        from post
        where post.post_id = ?;
    """
    sql_row_objs = query_db(sql_string, args=[post_id], one=True)
    return make_post(sql_row_objs)


def get_post_replies(post_id):
    sql_string = """
        select reply.*
        from reply
        where reply.reply_post_id = ?;
    """
    sql_row_objs = query_db(sql_string, args=[post_id])
    return make_replies(sql_row_objs)


def get_boards_posts(board_acronym):
    sql_string = """
        select post.*
        from board
            left join post on board.board_id = post.post_board_id
        where board_acronym = ?
        and post.post_id is not null
        order by post_id;
    """
    sql_row_objs = query_db(sql_string, args=[board_acronym])
    return make_posts(sql_row_objs)


def get_boards():
    sql_string = 'select * from board;'
    sql_row_obj = query_db(sql_string)
    boards = ([Board(*board) for board in sql_row_obj]) if sql_row_obj else None
    return boards


def get_board_id(board_acronym):
    sql_string = 'select board_id from board where board_acronym = ?'
    board_id = query_db(sql_string, args=[board_acronym], one=True)['board_id']
    return board_id


def create_post(post_board_id, post, img_filename, img_uniqid, ip):
    try:
        user = ip
        sql_string = """insert into post(post_board_id, user, date, post, img_filename, img_uniqid)
                            values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""
        img_filename, post = make_none(img_filename, post)
        
        db = get_db()
        cur = db.cursor()
        cur.execute(sql_string, [post_board_id, user, post, img_filename, img_uniqid])
        db.commit()
        cur.close()
    except Exception as e:
        raise ValueError(e) from None


def create_reply(reply_post_id, reply, img_filename, img_uniqid, ip):
    try:
        user = ip
        sql_string = """insert into reply(reply_post_id, user, date, reply, img_filename, img_uniqid)
                            values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""
        img_filename, reply = make_none(img_filename, reply)
        
        db = get_db()
        cur = db.cursor()
        cur.execute(sql_string, [reply_post_id, user, reply, img_filename, img_uniqid])
        db.commit()
        cur.close()
    except Exception as e:
        raise ValueError(e) from None
