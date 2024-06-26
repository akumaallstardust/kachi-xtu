CREATE TABLE user_data_table(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username varchar(100),
    user_profile varchar(500) NOT NULL DEFAULT (''),
    deleted_flag varchar(10) NOT NULL DEFAULT "n",
    guest_flag VARCHAR(10) NOT NULL DEFAULT 'n'
);

CREATE TABLE user_secret_data_table(
    user_id INT PRIMARY KEY,
    mailaddress varchar(256),
    password varchar(1024)
);

CREATE TABLE user_session_table(
    user_id INT,
    session_id_1 bigint PRIMARY KEY,
    session_id_2 bigint,
    user_agent varchar(1024),
    ip_address varchar(780) NOT NULL DEFAULT '',
    is_app varchar(10) NOT NULL DEFAULT "n",
    uniqueid VARCHAR(200) NOT NULL DEFAULT '',
    last_access_time DATETIME
);

CREATE TABLE user_view_history(
    user_id INT PRIMARY KEY,
    view_history_today mediumtext NOT NULL DEFAULT (''),
    view_history_resent_100 text NOT NULL DEFAULT ('')
);

CREATE TABLE user_review_history(
    user_id INT PRIMARY KEY,
    like_history mediumtext NOT NULL DEFAULT (''),
    dislike_history mediumtext NOT NULL DEFAULT ('')
);

CREATE TABLE user_setting_table(
    user_id INT PRIMARY KEY,
    auto_comment_open varchar(10) NOT NULL DEFAULT "0",
    defalt_exclude_words text NOT NULL DEFAULT ('')
);

CREATE TABLE user_relation_table(
    user_id INT PRIMARY KEY,
    followers mediumtext NOT NULL DEFAULT (''),
    followed_users mediumtext NOT NULL DEFAULT (''),
    followers_count int NOT NULL DEFAULT 0,
    followed_user_count int NOT NULL DEFAULT 0
);

CREATE TABLE user_notification_table(
    user_id INT PRIMARY KEY,
    notification_list json DEFAULT NULL,
    excluded_notification_ids mediumtext NOT NULL DEFAULT (''),
    exist_unread_notification_flag varchar(10) NOT NULL DEFAULT "n"
);

#{notification_id:str,notification_content:str,notification_read_flag:str}任意でnotification_main_content
CREATE TABLE post_data_table(
    content_id INT AUTO_INCREMENT PRIMARY KEY,
    title varchar(50),
    content mediumtext,
    user_id int,
    overview varchar(500),
    word_count int,
    tags varchar(500),
    post_date DATETIME,
    notification_user_ids mediumtext NOT NULL DEFAULT (''),
    deleted_flag varchar(10) NOT NULL DEFAULT "n"
);

CREATE TABLE deleted_post_data_table AS
SELECT
    *
FROM
    post_data_table;

CREATE TABLE post_view_count_table(
    content_id INT PRIMARY KEY,
    view_count bigint NOT NULL DEFAULT 0,
    hour int NOT NULL DEFAULT 0,
    hour_joined_23 varchar(500) NOT NULL DEFAULT "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
    day int NOT NULL DEFAULT 0,
    day_joined_29 varchar(900) NOT NULL DEFAULT "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
    week int NOT NULL DEFAULT 0,
    month_30 int NOT NULL DEFAULT 0
);

CREATE TABLE post_review_table(
    content_id INT PRIMARY KEY,
    like_count int NOT NULL DEFAULT 0,
    like_count_hour int NOT NULL DEFAULT 0,
    like_count_hour_joined_23 varchar(500) NOT NULL DEFAULT "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
    like_count_day int NOT NULL DEFAULT 0,
    like_count_day_joined_29 varchar(900) NOT NULL DEFAULT "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
    like_count_week int NOT NULL DEFAULT 0,
    like_count_month_30 int NOT NULL DEFAULT 0,
    dislike_count int NOT NULL DEFAULT 0,
    dislike_count_hour int NOT NULL DEFAULT 0,
    dislike_count_hour_joined_23 varchar(500) NOT NULL DEFAULT "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
    dislike_count_day int NOT NULL DEFAULT 0,
    dislike_count_day_joined_29 varchar(900) NOT NULL DEFAULT "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
    dislike_count_week int NOT NULL DEFAULT 0,
    dislike_count_month_30 int NOT NULL DEFAULT 0,
    like_dislike_ratio DOUBLE NOT NULL DEFAULT 1
);

CREATE TABLE post_discussion_table(
    content_id INT PRIMARY KEY,
    comment_ids mediumtext NOT NULL DEFAULT ('')
);

CREATE TABLE discussion_data_table(
    comment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    content text NOT NULL DEFAULT (''),
    parent_content_id int,
    parent_comment_id bigint,
    user_id int,
    post_date DATETIME,
    notification_user_ids mediumtext NOT NULL DEFAULT (''),
    deleted_flag varchar(10) NOT NULL DEFAULT "n"
);

CREATE TABLE discussion_review_table(
    comment_id BIGINT PRIMARY KEY,
    like_count int NOT NULL DEFAULT 0,
    dislike_count int NOT NULL DEFAULT 0
);

CREATE TABLE report_table(
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    report_user_id int,
    report_category text NOT NULL DEFAULT (''),
    report_comment text NOT NULL DEFAULT (''),
    resolved int NOT NULL DEFAULT 0
);

CREATE TABLE other_values_table (
    id int NOT NULL DEFAULT 1,
    update_hour_count int NOT NULL DEFAULT 0
);

INSERT INTO
    `other_values_table`(`id`, `update_hour_count`)
VALUES
    ('1', '0');