# dbapi

豆瓣命令行客户端

## 安装

```bash
pip3 install dbapi
```

## 使用

```bash
dbapi --help
Usage:
    dbapi <api> [options...]
    dbapi <module> <api> [options...]

Available API:
 - ck 
 - expire 
 - flush 
 - json <url> <method> <params> <data>
 - load 
 - login <username> <password>
 - logout 
 - persist 
 - req <url> <method> <params> <data> <auth>
 - toJSON 
 - to_xml <content> <kwargs>
 - use <cookies>
 - xml <url> <method> <params> <data>
 - group
    - group add_comment <topic_id> <content> <reply_id>
    - group add_group <kwargs>
    - group add_topic <group_alias> <title> <content>
    - group get_topic <topic_id>
    - group join_group <group_alias> <message>
    - group leave_group <group_alias>
    - group like_topic <topic_id>
    - group list_commented_topics <start>
    - group list_comments <topic_id> <start>
    - group list_joined_groups <user_alias>
    - group list_joined_topics <start>
    - group list_liked_topics <user_alias> <start>
    - group list_reced_topics <user_alias> <start>
    - group list_topics <group_alias> <_type> <start>
    - group list_user_comments <topic_id> <user_alias>
    - group list_user_topics <start>
    - group rec_topic <topic_id>
    - group remove_comment <topic_id> <comment_id> <reason> <other>
    - group remove_commented_topic <topic_id>
    - group remove_group <group_id>
    - group remove_topic <topic_id>
    - group search_groups <keyword> <start>
    - group search_topics <keyword> <sort> <start>
    - group toJSON 
    - group undo_like_topic <topic_id>
    - group undo_rec_topic <rec_id>
    - group update_topic <topic_id> <title> <content>
 - people
    - people add_album <kwargs>
    - people add_album_comment <kwargs>
    - people add_photo <kwargs>
    - people add_photo_comment <photo_id> <content>
    - people add_status <kwargs>
    - people get_album <album_id>
    - people get_people <user_alias>
    - people get_photo <photo_id>
    - people like_photo <photo_id>
    - people like_status <status_id>
    - people list_albums <user_alias>
    - people list_contacts <user_alias> <start>
    - people list_photo_comments <photo_id> <start>
    - people list_photo_likes <photo_id> <start>
    - people list_photo_recs <photo_id> <start>
    - people list_photos <album_id>
    - people list_rev_contacts <user_alias> <start>
    - people list_status_comments <user_alias> <start>
    - people list_statuses <user_alias> <start>
    - people rec_photo <photo_id>
    - people remove_album <album_id>
    - people remove_album_comment <kwargs>
    - people remove_photo <photo_id>
    - people remove_photo_comment <comment_id>
    - people remove_status <status_id>
    - people toJSON 
    - people undo_like_photo <photo_id>
    - people undo_like_status <status_id>
    - people undo_rec_photo <photo_id>
    - people update_album <kwargs>
```

## License

MIT