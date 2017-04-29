#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: relation.
import atexit
import json
import os
import time
from sys import argv

from dbapi.DoubanAPI import DoubanAPI


class RelationSpider(object):
    def __init__(self, **kwargs):
        self._persist_file = kwargs.get('persist_file', '__relation__.json')  # 持久化文件
        self._persist_step = kwargs.get('persist_step', 100)  # 爬N个用户后持久化一次
        self._min_rev = int(kwargs.get('min_rev', 500))
        _init_users = kwargs.get('init_users', '')  # 种子用户，只有用户ID
        self._init_users = _init_users.split(',') if _init_users else []
        self._api = DoubanAPI()
        self._users_list = []  # 过滤出来的需要继续爬的用户列表，只保存ID
        self._users_dict = {}  # 爬过的用户字典
        self._parsing = None
        self._step = 0
        atexit.register(self.abort)
        self.load()
        self.init()

    def abort(self):
        self._api.logger.info('spider aborted when parsing: %s' % self._parsing)
        self.reset_alias(self._parsing)
        self.persist()

    def add_alias(self, alias):
        if not alias:
            return
        if alias in self._users_dict:
            return
        try:
            user = self._api.people.get_people(alias)
        except Exception as e:
            self._api.logger.error('get user <%s> error: %s' % (alias, e))
            return
        time.sleep(.8)  # 防验证码
        if not user:
            return
        self._api.logger.debug('spider add user<%s> contact_count<%s> rev_contact_count<%s>'
                               % (user['alias'], user['contact_count'], user['rev_contact_count']))
        user['parsed'] = False
        self._users_dict[alias] = user
        if user['rev_contact_count'] > self._min_rev:
            self._users_list.append(user['alias'])
        self._step += 1
        if self._step > self._persist_step:
            self.persist()
            self._step = 0

    def reset_alias(self, alias):
        if alias in self._users_dict:
            self._users_dict[alias]['parsed'] = False
            if alias not in self._users_list:
                self._users_list.append(alias)

    def next_alias(self):
        if not self._users_list:
            return None
        alias = self._users_list.pop(0)
        self._users_dict[alias]['parsed'] = True
        self._parsing = alias
        return alias

    def next(self):
        alias = self.next_alias()
        if not alias:
            return
        self._api.logger.debug('spider start parse user<%s>' % alias)
        next_start = 0
        try:
            while next_start is not None:
                contacts = self._api.people.list_contacts(alias, next_start)
                next_start = contacts['next_start']
                for user in contacts['results']:
                    self.add_alias(user['alias'])
        except Exception as e:
            self._api.logger.error('parse user <%s> error: %s' % (alias, e))
            self.reset_alias(alias)
        self.next()

    def init(self):
        for alias, user in self._users_dict.items():
            if user['rev_contact_count'] > self._min_rev and not user.get('parsed'):
                self._users_list.append(alias)
        for alias in self._init_users:
            self.add_alias(alias)
        self._api.logger.debug('spider init with users<%s>' % self._init_users)

    def load(self):
        if os.path.isfile(self._persist_file):
            with open(self._persist_file, 'r') as f:
                self._users_dict = json.load(f) or {}

    def persist(self):
        with open(self._persist_file, 'w+') as f:
            self._api.logger.info('spider persist data, size: %s' % len(self._users_dict))
            json.dump(self._users_dict, f)


if __name__ == '__main__':
    spider = RelationSpider(**dict([arg.split('=', 1) for arg in argv[1:]]))
    spider.next()
