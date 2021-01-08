import random

from .db import Board, Post, Reply, get_db, query_db
from .utils import get_file_ext


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
    sql_row_objs = query_db(sql_string, args=[post_id])
    post = (
        ([Post(*p, get_file_ext(p[5])) for p in sql_row_objs][0])
        if sql_row_objs
        else None
    )
    return post


def get_post_replies(post_id):
    sql_string = """
        select reply.*
        from reply
        where reply.reply_post_id = ?;
    """
    sql_row_objs = query_db(sql_string, args=[post_id])
    replies = (
        ([Reply(*r, get_file_ext(r[5])) for r in sql_row_objs])
        if sql_row_objs
        else None
    )
    return replies


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
    posts = (
        ([Post(*p, get_file_ext(p[5])) for p in sql_row_objs]) if sql_row_objs else None
    )
    return posts


def get_boards():
    sql_string = 'select * from board;'
    sql_row_obj = query_db(sql_string)
    boards = ([Board(*board) for board in sql_row_obj]) if sql_row_obj else None
    return boards


def create_post(post_board_id, post, img_filename, img_uniqid):
    try:
        user = 'anon' + str(random.randint(10_000, 99_999))
        sql_string = """insert into post(post_board_id, user, date, post, img_filename, img_uniqid)
                            values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""
        db = get_db()
        cur = db.cursor()
        if img_filename == '':
            img_filename = None
        if post == '':
            post = None
        cur.execute(sql_string, [post_board_id, user, post, img_filename, img_uniqid])
        db.commit()
        cur.close()
        return cur.lastrowid
    except Exception as e:
        raise ValueError(e) from None


def create_reply(reply_post_id, reply, img_filename, img_uniqid):
    try:
        user = 'anon' + str(random.randint(10_000, 99_999))
        sql_string = """insert into reply(reply_post_id, user, date, reply, img_filename, img_uniqid)
                            values (?, ?, strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), ?, ?, ?);"""
        db = get_db()
        cur = db.cursor()
        if img_filename == '':
            img_filename = None
        if reply == '':
            reply = None
        cur.execute(sql_string, [reply_post_id, user, reply, img_filename, img_uniqid])
        db.commit()
        cur.close()
        return cur.lastrowid
    except Exception as e:
        raise ValueError(e) from None
