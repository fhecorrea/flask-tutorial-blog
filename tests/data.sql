INSERT INTO user (alias, email, passwd) VALUES
('Silva', 'silva@mail.com', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
('Agosto', 'august@doin.it', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO post (title, body, author_id, created) VALUES
('My first post', "Hello, my name\'s Silva and this is my first post on this site.", 1, "2018-06-18 09:35:45"),
('Political troubles: a real threat', "Hello everybody." || x'0a' || "Too long, you didn't read.", 1, "2018-06-27 06:01:32"),
('Many troubles...', "In this post, we are going to talk about something.", 1, "2018-07-06 18:13:12"),
('My debut', "Hi, my name is Agosto and I am starting as a editor on this site", 2, "2018-07-16 19:59:51");