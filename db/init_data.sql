insert into board(board_acronym, board_description) values ('g', 'Technology');--board_id=1
insert into board(board_acronym, board_description) values ('ck', 'Food & Cooking');--board_id=2
insert into board(board_acronym, board_description) values ('b', 'Random');--board_id=3


insert into post(post_board_id, user, date, post, img_filename, img_uniqid)
    values (1, 'anon11111', strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), 'roll', null, null);
insert into post(post_board_id, user, date, post, img_filename, img_uniqid)
    values (1, 'anon22222', strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), 'roll', null, null);


insert into reply(reply_post_id, user, date, reply, img_filename, img_uniqid)
    values (2, "anon12345", strftime('%Y-%m-%d %H:%M', 'now', 'localtime'), "reply 1", null, null);
