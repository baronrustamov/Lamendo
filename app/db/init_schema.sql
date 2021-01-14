create table board (
    board_id integer primary key,
    board_acronym text not null,
    board_description text not null
);


create table post (
    post_id integer primary key,
    post_board_id integer,
    user text not null,
    date text not null,
    post text,
    img_filename text,
    img_uid text,
    foreign key(post_board_id) references board(board_id)
);


create table reply (
    reply_id integer primary key,
    reply_post_id integer,
    user text not null,
    date text not null,
    reply text,
    img_filename text,
    img_uid text,
    foreign key(reply_post_id) references post(post_id)
);

create table event (
    event_id integer primary key,
    ip text not null,
    last_event_date integer default (strftime('%s', 'now')) not null,-- seconds since epoch
    blacklisted integer default 0 not null,-- 0 false, 1 true
    blacklisted_until integer
);
