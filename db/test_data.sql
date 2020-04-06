-- create table board (
--     board_id integer primary key,
--     board_acronym text not null,
--     board_description text not null
-- );
insert into board(board_acronym, board_description) values ('g', 'Technology');--board_id=1
insert into board(board_acronym, board_description) values ('ck', 'Food & Cooking');--board_id=2
insert into board(board_acronym, board_description) values ('b', 'Random');--board_id=3


-- create table post (
--     post_id integer primary key,
--     post_board_id integer,
--     user text not null,
--     date text not null,
--     post text,
--     img_filename text,
--     img_uniqid text,
--     foreign key(post_board_id) references board(board_id)
-- );
insert into post(post_board_id, user, date, post, image_filename, image_uniqid)
    values (1, 'anon11111', strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), 'roll', null, null);
insert into post(post_board_id, user, date, post, image_filename, image_uniqid)
    values (2, 'anon22222', strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), 'roll', null, null);
insert into post(post_board_id, user, date, post, image_filename, image_uniqid)
    values (3, 'anon33333', strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), 'roll', null, null);


-- create table reply (
--     reply_id integer primary key,
--     reply_post_id integer,
--     user text not null,
--     date text not null,
--     reply text,
--     img_filename text,
--     img_uniqid text,
--     foreign key(reply_post_id) references post(post_id)
-- );
