#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: relation.
import atexit
import gc
import json
import logging
import os
import sys
import time
from sys import argv
from threading import Thread

import psutil

from dbapi.DoubanAPI import DoubanAPI
from dbapi.endpoints import API_PEOPLE_HOME


class Worker:
    def __init__(self, username, password=None, cookies=None, spider=None):
        """
        :param username: 
        :param password: 
        :param cookies:
         
        :type spider: RelationSpider
        :param spider: 
        """
        self.id = username
        api = DoubanAPI(logger=username, persist_file='__cache__' + username + '.json')
        if api.user_alias is None:
            if cookies:
                api.use(cookies)
            if api.user_alias is None and password:
                api.login(username, password)
        time.sleep(1)
        self.api = api
        self.spider = spider
        self.parsing = None
        self.killing = False

        self.thread = None
        """:type: Thread"""

    def run(self):
        while True:
            if self.spider.running is False:
                return self.stop('spider stopped')
            if self.killing is True:
                return self.stop('worker killed')
            alias = self.spider.next_alias()
            if alias is None:
                return self.stop('no more user to parse')
            self.parsing = alias
            self.api.logger.debug('spider start parse user<%s>' % alias)
            next_start = 0
            try:
                while next_start is not None:
                    if self.spider.running is False:
                        self.spider.reset_alias(alias)
                        return self.stop('spider stopped when parse %s[%s]' % (alias, next_start))
                    if self.killing is True:
                        self.spider.reset_alias(alias)
                        return self.stop('worker killed when parse %s[%s]' % (alias, next_start))
                    contacts = self.api.people.list_contacts(alias, next_start)
                    next_start = contacts['next_start']
                    for item in contacts['results']:
                        if self.spider.has_alias(item['alias']):
                            continue
                        if self.spider.running is False:
                            self.spider.reset_alias(alias)
                            return self.stop('spider stopped when parse %s, %s' % (alias, item['alias']))
                        if self.killing is True:
                            self.spider.reset_alias(alias)
                            return self.stop('worker killed when parse %s, %s' % (alias, item['alias']))
                        try:
                            user = self.api.people.get_people(item['alias'])
                            if user is None:
                                self.spider.report_alias(item['alias'])
                            elif self.spider.add_user(user):
                                self.api.logger.debug(
                                    'add user<%s> contact_count<%s> rev_contact_count<%s>'
                                    % (user['alias'], user['contact_count'], user['rev_contact_count']))
                        except Exception as e:
                            self.api.logger.exception('get user <%s> error: %s' % (item['alias'], e))
                        time.sleep(3)  # 防验证码
                self.spider.done_alias(alias)
                time.sleep(3)
            except Exception as e:
                self.api.logger.exception('parse user <%s> error: %s' % (alias, e))
                # 不能在循环中捕获，虽然更高效，但是可能会死循环
                self.spider.reset_alias(alias)

    @property
    def running(self):
        return self.thread is not None and self.thread.is_alive()

    def stop(self, reason, join=False):
        if self.thread is None:
            return
        self.api.logger.debug('worker thread <%s> with <%s> stopped for <%s>' % (self.thread.ident, self.id, reason))
        self.killing = True
        join and self.thread.join()
        self.thread = None
        self.killing = False

    def start(self):
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()
        self.api.logger.debug('worker thread <%s> with <%s> started' % (self.thread.ident, self.id))

    def reload(self):
        self.stop('reload', True)
        self.start()


def mb(value):
    return value / 1024 / 1024


class RelationSpider(object):
    """
    目前想当然的从操作上避免并发
    """

    def __init__(self, **kwargs):
        """持久化文件"""
        self.persist_file = kwargs.get('persist_file', '__relation__.json')
        """:type: str"""

        """爬N个用户后持久化一次"""
        self.persist_step = kwargs.get('persist_step', 100)
        """:type: int"""

        """储存分析结果的文件"""
        self.result_file = kwargs.get('result_file', '__result__.json')
        """:type: str"""

        """关注者最小值"""
        self.min_rev = int(kwargs.get('min_rev', 10000))
        """:type: int"""

        init_users = kwargs.get('init_users')
        """:type: str"""
        """种子用户，只有用户ID"""
        self.init_users = init_users.split(',') if init_users else []
        """:type: dict[str]"""

        """过滤出来的需要继续爬的用户列表，只保存ID，pop和append都是安全的"""
        self.users_list = set()
        """:type: set[str]"""

        """爬过的用户字典，需要保证在persist时不被写入(所以在运行中persist有问题！)"""
        self.users_dict = {}
        """:type: dict[dict]"""

        """爬取出错的用户"""
        self.reports_dict = {}
        """:type: dict[str, dict]"""

        self.step = 0
        """:type: int"""

        """是否已开始"""
        self.running = False
        """:type: bool"""

        """赋值操作具有原子性，可保线程安全，保证在persist时user_dict不被写入"""
        self.persisting = False
        """:type: bool"""

        logger = logging.getLogger('spider:relation')
        if len(logger.handlers) is 0:
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
        self.logger = logger

        """爬虫表"""
        self.workers = []
        """:type: list[Worker]"""

        with open(kwargs.get('accounts_file', 'accounts.dat'), 'r') as f:
            [self.add_worker(*item.strip().split(':', 2)) for item in f.read().split('\n') if item]

        self.load()

        atexit.register(self.stop)

    def add_worker(self, username, password=None, cookies=None):
        worker = Worker(username, password, cookies, self)
        if worker.api.user_alias is not None:
            self.workers.append(worker)

    def should_parse(self, user):
        """
        :type user: dict
        :param user: 
        
        :return: 
        """
        return self.min_rev < user['rev_contact_count'] and not user.get('parsed', False)

    def load(self):
        if os.path.isfile(self.persist_file):
            with open(self.persist_file, 'r') as f:
                data = json.load(f) or {}
                self.users_dict = data.get('users_dict', {})
                self.reports_dict = data.get('reports_dict', {})
        [self.users_list.add(alias) for (alias, user) in self.users_dict.items() if self.should_parse(user)]
        [self.users_list.add(alias) for alias in self.init_users if
         alias not in self.users_dict and alias not in self.reports_dict]

    def persist(self):
        self.persisting = True

        def persist():
            with open(self.persist_file, 'w+') as f:
                self.logger.info('spider persist data, size: %s' % len(self.users_dict))
                json.dump({
                    'users_dict': self.users_dict,
                    'reports_dict': self.reports_dict,
                }, f, indent=2)
            with open(self.result_file, 'w+') as f:
                json.dump(self.summary(), f, indent=2)

        thread = Thread(target=persist)
        thread.start()
        thread.join()
        self.persisting = False

    def start(self):
        if len(self.workers) is 0:
            raise Exception('Cannot start spider without worker')
        self.running = True
        [item.start() for item in self.workers]
        ps = psutil.Process(os.getpid())
        while True:
            time.sleep(1800)  # half hour
            rss = ps.memory_info().rss
            if rss > 1 << 25:
                [item.reload() for item in self.workers]
                gc.collect()
                self.logger.warning('memory overflow, before is <%s>, after is <%s>'
                                    % (mb(rss), mb(ps.memory_info().rss)))

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.logger.info('spider aborted when parsing<%s>' % [item.parsing for item in self.workers])
        [self.reset_alias(item.parsing) for item in self.workers]
        self.persist()

    def add_user(self, user):
        """
        将获取到Profile的用户添加进来
        需要防止在persist的时候写入，否则会写入失败！
        
        :type user: dict
        :param user: 
        
        :rtype: bool
        :return: 
        """
        if self.persisting or not user or user['alias'] in self.users_dict:
            return False
        user['parsed'] = False
        self.users_dict[user['alias']] = user
        if self.should_parse(user):
            self.users_list.add(user['alias'])
            self.wake_up()
        self.step += 1
        if self.step > self.persist_step:
            self.persist()
            self.step = 0
        return True

    def wake_up(self):
        for item in self.workers:
            if item.running is False:
                item.start()

    def report_alias(self, alias):
        if alias not in self.reports_dict:
            self.reports_dict[alias] = {
                'count': 1,
                'alias': alias,
                'url': API_PEOPLE_HOME % alias,
            }
        else:
            self.reports_dict[alias]['count'] += 1

    def has_alias(self, alias):
        """
        判断是否已爬取过用户
        
        :type alias: str
        :param alias: 
        
        :rtype: bool
        :return: 
        """
        return alias in self.users_dict or (alias in self.reports_dict and self.reports_dict[alias]['count'] > 0)

    def reset_alias(self, alias):
        if alias in self.users_dict:
            self.users_dict[alias]['parsed'] = False
            if alias not in self.users_list:
                self.users_list.add(alias)

    def next_alias(self):
        if len(self.users_list) is 0:
            return None
        alias = self.users_list.pop()
        return alias

    def done_alias(self, alias):
        if alias in self.users_dict:
            self.users_dict[alias]['parsed'] = True

    def summary(self):
        total = len(self.users_dict)
        results = []
        for alias, user in self.users_dict.items():
            if user['rev_contact_count'] > self.min_rev:
                results.append(user)
        results.sort(key=lambda item: item['rev_contact_count'], reverse=True)
        return {'results': results, 'total': total, 'filtered': len(results)}


def test():
    spider = RelationSpider(**dict([arg.split('=', 1) for arg in argv[1:]]))
    spider.start()


if __name__ == '__main__':
    test()
