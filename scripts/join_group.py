#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2018 acrazing <joking.young@gmail.com>. All rights reserved.
# @since 2018-12-03 00:03:40
import time

from dbapi.DoubanAPI import DoubanAPI


class GroupAPI:
    def __init__(self):
        self.api = DoubanAPI(flush=False)
        self._applied = {}
        self._users = {}

    def run(self):
        self.api.flush()
        groups = self.api.group.list_joined_groups()['results']
        for group in groups:
            self._applied[group['alias']] = True
        self.handle_user(self.api.user_alias)

    def handle_user(self, user_alias):
        self.join_user_groups(user_alias)
        users = self.api.people.list_contacts()['results']
        for user in users:
            if self._users.get(user['alias'], None) is None:
                self.handle_user(user['alias'])
                self._users[user['alias']] = True
                time.sleep(30)
            else:
                print('skip user: %s' % (user['alias']))

    def join_user_groups(self, user_alias):
        groups = self.api.group.list_joined_groups(user_alias)['results']
        for group in groups:
            if self._applied.get(group['alias'], None) is None:
                self.api.group.join_group(group['alias'], 'Hello ~')
                self._applied[group['alias']] = True
                time.sleep(30)
            else:
                print('skip group: %s' % (group['alias']))


if __name__ == '__main__':
    group = GroupAPI()
    group.run()
