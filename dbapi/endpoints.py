#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: endpoints.
"""
API接口列表
"""

API_HOME = 'https://douban.com/'
API_ACCOUNT_LOGIN = 'https://www.douban.com/accounts/login'
API_ACCOUNT_HOME = 'https://www.douban.com/mine/'
API_ACCOUNT_LOGOUT = 'https://www.douban.com/accounts/logout?source=group&ck=%s'
API_GROUP_SEARCH_GROUPS = 'https://www.douban.com/group/search?start=%s&cat=1019&sort=relevance&q=%s'
API_GROUP_LIST_JOINED_GROUPS = 'https://www.douban.com/group/people/%s/joins'
API_GROUP_GROUP_HOME = 'https://www.douban.com/group/%s/'
API_GROUP_LIST_GROUP_TOPICS = 'https://www.douban.com/group/%s/discussion'
API_GROUP_LIST_USER_PUBLISHED_TOPICS = 'https://www.douban.com/group/people/%s/publish'
API_GROUP_LIST_USER_COMMENTED_TOPICS = 'https://www.douban.com/group/people/%s/reply'
API_GROUP_LIST_USER_LIKED_TOPICS = 'https://www.douban.com/group/people/%s/likes'
API_GROUP_LIST_USER_RECED_TOPICS = 'https://www.douban.com/group/people/%s/recommendations'
API_GROUP_SEARCH_TOPICS = 'https://www.douban.com/group/search?start=%s&cat=1013&sort=%s&q=%s'
API_GROUP_ADD_TOPIC = 'https://www.douban.com/group/%s/new_topic'
API_GROUP_HOME = 'https://www.douban.com/group/'
API_GROUP_GET_TOPIC = 'https://www.douban.com/group/topic/%s/'
API_GROUP_REMOVE_TOPIC = 'https://www.douban.com/group/topic/%s/remove'
API_GROUP_UPDATE_TOPIC = 'https://www.douban.com/group/topic/%s/edit'
API_GROUP_REMOVE_COMMENT = 'https://www.douban.com/j/group/topic/%s/remove_comment'
API_GROUP_ADMIN_REMOVE_COMMENT = 'https://www.douban.com/group/topic/%s/remove_comment'
API_GROUP_ADD_COMMENT = 'https://www.douban.com/group/topic/%s/add_comment'

API_PEOPLE_HOME = 'https://www.douban.com/people/%s/'
API_PEOPLE_LIST_CONTACTS = 'https://www.douban.com/contacts/list'
API_PEOPLE_LIST_REV_CONTACTS = 'https://www.douban.com/contacts/rlist'
API_PEOPLE_LIST_USER_CONTACTS = 'https://www.douban.com/people/%s/contacts'
API_PEOPLE_LIST_USER_REV_CONTACTS = 'https://www.douban.com/people/%s/rev_contacts'
