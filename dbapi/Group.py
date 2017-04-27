#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: Group.
import re
import traceback

from dbapi.BaseAPI import BaseAPI
from dbapi.endpoints import API_GROUP_SEARCH_GROUPS


class Group(BaseAPI):
    # 创建小组
    def add_group(self, **kwargs):
        raise NotImplementedError()

    # 搜索小组
    def search_groups(self, keyword, start=0):
        xml = self._xml(API_GROUP_SEARCH_GROUPS % (start, keyword))
        xml_results = xml.xpath('//div[@class="groups"]/div[@class="result"]')
        results = []
        for item in xml_results:
            try:
                url = item.xpath('.//h3/a/@href')[0]
                info = item.xpath('.//div[@class="content"]/div[@class="info"]/text()')[0].strip(' ')
                onclick = item.xpath('.//h3/a/@onclick')[0]
                meta = {
                    'icon': item.xpath('.//img/@src')[0],
                    'id': re.search(r'sid[^\d]+(\d+)', onclick).groups()[0],
                    'url': url,
                    'alias': url.rstrip('/').rsplit('/', 1)[1],
                    'title': item.xpath('.//h3/a/text()')[0],
                    'user_count': int(re.match(r'\d+', info).group()),
                    'user_alias': re.search(r'个(.+)\s*在此', info).groups()[0],
                }
                results.append(meta)
            except Exception as e:
                print('parse result error: %s' % e, traceback.print_exc())
        xml_count = xml.xpath('//div[@class="paginator"]/span[@class="count"]/text()')
        total = 0
        try:
            total = int(re.search(r'共(\d+)个', xml_count[0]).groups()[0])
        except:
            pass
        return {'results': results, 'total': total}

    # 加入的小组列表
    def list_joined_groups(self, start=0, user_id=None):
        pass

    # 删除小组
    def remove_group(self, group_id):
        pass

    # 加入小组
    def join_group(self, group_id, reason=None):
        pass

    # 离开小组
    def leave_group(self, group_id):
        pass

    # 搜索话题
    def search_topics(self, keyword, start=0):
        pass

    # 已加入小组的所有话题
    def list_joined_topics(self, start=0, user_id=None):
        pass

    # 小组内的话题
    def list_topics(self, group_id, start=0):
        pass

    # 发表的话题
    def list_user_topics(self, start=0, user_id=None):
        pass

    # 回复过的话题列表
    def list_commented_topics(self, start=0):
        pass

    # 推荐的话题列表
    def list_recommended_topics(self, start=0):
        pass

    # 喜欢的话题列表
    def list_liked_topics(self, start=0):
        pass

    # 创建话题
    def add_topic(self, group_id, title, content):
        pass

    # 删除话题
    def remove_topic(self, topic_id):
        pass

    # 编辑话题
    def update_topic(self, topic_id, title, content):
        pass

    # 推荐话题
    def rec_topic(self, topic_id):
        pass

    # 喜欢话题
    def like_topic(self, topic_id):
        pass

    # 回复列表
    def list_comments(self, topic_id, start=0):
        pass

    # 添加回复
    def add_comment(self, topic_id, content, reply_id):
        pass

    # 删除回复
    def remove_comment(self, comment_id):
        pass
