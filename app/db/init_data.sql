insert into board(board_acronym, board_description) values ('A', 'Art');--board_id=1
insert into board(board_acronym, board_description) values ('R', 'Random');--board_id=2
insert into board(board_acronym, board_description) values ('T', 'Tech');--board_id=3

insert into post(post_board_id, user, date, post, img_filename, img_uid, ip)
    values (1, '111ppe9228edfe', strftime('%Y-%m-%d %H:%M', 'now'), 'This is the FIRST post.', null, null, "1.2.3.4");

insert into post(post_board_id, user, date, post, img_filename, img_uid, ip)
    values (1, '222ppe9228edfe', strftime('%Y-%m-%d %H:%M', 'now'), 'This is the SECOND post.', null, null, "1.2.3.4");


insert into reply(reply_post_id, parent_reply_id, user, date, reply, img_filename, img_uid, ip)
    values (1, null, "0000rre9228edfe", strftime('%Y-%m-%d %H:%M', 'now'), "This is the FIRST reply.", "12345.png", "1a2b3c4d5e", "1.2.3.4");

insert into reply(reply_post_id, parent_reply_id, user, date, reply, img_filename, img_uid, ip)
    values (1, 1, "1111rrv9228edfe", strftime('%Y-%m-%d %H:%M', 'now'), "Replying to FIRST reply.", null, null, "1.2.3.4");

insert into reply(reply_post_id, parent_reply_id, user, date, reply, img_filename, img_uid, ip)
    values (1, null, "2222rrv9228edfe", strftime('%Y-%m-%d %H:%M', 'now'), "This is the SECOND reply.", null, null, "1.2.3.4");

insert into reply(reply_post_id, parent_reply_id, user, date, reply, img_filename, img_uid, ip)
    values (1, 1, "3333rrv9228edfe", strftime('%Y-%m-%d %H:%M', 'now'), "Replying to the FIRST reply AGAIN.", null, null, "1.2.3.4");

insert into reply(reply_post_id, parent_reply_id, user, date, reply, img_filename, img_uid, ip)
    values (1, 1, "4444rrv9228edfe", strftime('%Y-%m-%d %H:%M', 'now'), "Replying to the FIRST reply AGAIN x2.", null, null, "1.2.3.4");

insert into reply(reply_post_id, parent_reply_id, user, date, reply, img_filename, img_uid, ip)
    values (1, 1, "5555rrv9228edfe", strftime('%Y-%m-%d %H:%M', 'now'), "Replying to the FIRST reply AGAIN x3.", null, null, "1.2.3.4");

insert into reply(reply_post_id, parent_reply_id, user, date, reply, img_filename, img_uid, ip)
    values (1, 1, "6666rrv9228edfe", strftime('%Y-%m-%d %H:%M', 'now'), "Replying to the FIRST reply AGAIN x4.", null, null, "1.2.3.4");

insert into reply(reply_post_id, parent_reply_id, user, date, reply, img_filename, img_uid, ip)
    values (1, 1, "7777rrv9228edfe", strftime('%Y-%m-%d %H:%M', 'now'), "Replying to the FIRST reply AGAIN x5.", null, null, "1.2.3.4");

insert into event(event_id, ip, last_event_date, blacklisted)
    values (1, '1.2.3.4', 1610472923, 0);
