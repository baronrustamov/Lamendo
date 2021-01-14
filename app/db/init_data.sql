insert into board(board_acronym, board_description) values ('A', 'Art');--board_id=1
insert into board(board_acronym, board_description) values ('R', 'Random');--board_id=2
insert into board(board_acronym, board_description) values ('T', 'Tech');--board_id=3

insert into post(post_board_id, user, date, post, img_filename, img_uid)
    values (1, 'user11111', strftime('%Y-%m-%d %H:%M', 'now'), 'This is the FIRST post.', null, null);
insert into post(post_board_id, user, date, post, img_filename, img_uid)
    values (1, 'user22222', strftime('%Y-%m-%d %H:%M', 'now'), 'This is the SECOND post.', null, null);


insert into reply(reply_post_id, user, date, reply, img_filename, img_uid)
    values (1, "user33333", strftime('%Y-%m-%d %H:%M', 'now'), "This is the FIRST reply.", "12345.png", "1a2b3c4d5e");

insert into reply(reply_post_id, user, date, reply, img_filename, img_uid)
    values (1, "user33333", strftime('%Y-%m-%d %H:%M', 'now'), "This is the SECOND reply.", null, null);

insert into event(event_id, ip, last_event_date, blacklisted)
    values (1, 'test_ip', 1610472923, 0);