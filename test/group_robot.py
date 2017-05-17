#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @author acrazing - joking.young@gmail.com
# @version 1.0.0
# @since 2017-05-15 17:05:15
#
# group_robot.py
#
import re
import time
from sys import argv

from dbapi.DoubanAPI import DoubanAPI


class GroupRobot:
    def __init__(self):
        self.api = DoubanAPI(flush=False)

    def join_groups(self, starter=None):
        if starter is None:
            print(self.api.req('http://localhost:8000/hello/world', params={'a': 'b'}).text)
            return
        ignore = re.compile(r'租|代购|招聘|淘宝|宠物|语')
        users = self.api.people.list_contacts(starter).get('results', [])
        time.sleep(1)
        joined = {}
        for item in self.api.group.list_joined_groups().get('results', []):
            joined[item['name']] = True
            if item['user_count'] < 50000 or ignore.search(item['name']) is not None:
                self.api.group.leave_group(item['alias'])
                time.sleep(1)
        time.sleep(1)
        while True:
            user = users.pop()
            if user['alias'] in joined:
                continue
            joined[user['alias']] = True
            for item in self.api.group.list_joined_groups(user['alias']).get('results', []):
                if item['name'] not in joined and item['user_count'] > 50000 and ignore.search(item['name']) is None:
                    ret = self.api.group.join_group(group_alias=item['alias'], message=item['name'])
                    print('join group: %s, result: %s, alias: %s' % (item['name'].encode('utf-8'), ret, item['alias']))
                    joined[item['name']] = True
                    time.sleep(1)
            if len(users) < 100:
                users += self.api.people.list_contacts(user['alias']).get('results', [])
                time.sleep(1)

    def reply_topics(self):
        topics = self.api.group.list_joined_topics().get('results', [])


if __name__ == '__main__':
    GroupRobot().join_groups(argv[1] if len(argv) > 1 else None)
