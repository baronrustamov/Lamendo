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
    post text not null,
    image_file text,
    foreign key(post_board_id) references board(board_id)
);


create table reply (
    reply_id integer primary key,
    reply_post_id integer,
    user text not null,
    date text not null,
    post text not null,
    image_file text,
    foreign key(reply_post_id) references post(post_id)
);