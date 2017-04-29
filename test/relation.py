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
import traceback
from sys import argv
from threading import Thread

from dbapi.DoubanAPI import DoubanAPI
from dbapi.endpoints import API_PEOPLE_HOME


class Worker(Thread):
    """
    进行爬虫任务的Worker
    """

    def __init__(self, api, spider):
        """
        :type api: DoubanAPI
        :param api:  初始化过的API客户端
        
        :type spider: RelationSpider
        :param spider: 
        """
        super(Worker, self).__init__()
        self._api = api
        self._spider = spider
        self.setDaemon(True)

    def run(self):
        if not self._spider.running:
            return
        alias = self._spider.next_alias()
        if not alias:
            self._spider.sleep(self)
            return
        self._api.logger.debug('spider start parse user<%s>' % alias)
        next_start = 0
        try:
            while next_start is not None:
                contacts = self._api.people.list_contacts(alias, next_start)
                next_start = contacts['next_start']
                for item in contacts['results']:
                    if self._spider.has_alias(item['alias']):
                        continue
                    try:
                        user = self._api.people.get_people(item['alias'])
                        if not user:
                            self._spider.report(item['alias'])
                        elif self._spider.add_user(user):
                            self._api.logger.debug('add user<%s> contact_count<%s> rev_contact_count<%s>'
                                                   % (user['alias'], user['contact_count'], user['rev_contact_count']))
                    except Exception as e:
                        print(traceback.print_exc())
                        self._api.logger.error('get user <%s> error: %s' % (item['alias'], e))
                    time.sleep(2)  # 防验证码
            self._spider.done_alias(alias)
            time.sleep(2)
        except Exception as e:
            self._api.logger.error('parse user <%s> error: %s' % (alias, e))
            # 不能在循环中捕获，虽然更高效，但是可能会死循环
            self._spider.reset_alias(alias)
        self.run()


class RelationSpider(object):
    """
    目前想当然的从操作上避免并发
    """

    def __init__(self, **kwargs):
        self._persist_file = kwargs.get('persist_file', '__relation__.json')  # 持久化文件
        self._persist_step = kwargs.get('persist_step', 100)  # 爬N个用户后持久化一次
        self._result_file = kwargs.get('result_file', '__result__.json')  # 储存分析结果的文件
        self._min_rev = int(kwargs.get('min_rev', 10000))  # 关注者最小值
        init_users = kwargs.get('init_users', '')  # 种子用户，只有用户ID
        self._init_users = init_users.split(',') if init_users else []
        self._users_list = []  # 过滤出来的需要继续爬的用户列表，只保存ID，pop和append都是安全的
        self._users_dict = {}  # 爬过的用户字典，需要保证在persist时不被写入(所以在运行中persist有问题！)
        self._parsing = []  # 正在被爬关注用户的ID列表，append和remove是线程安全的(remove确定吗?)
        self._reports_dict = {}  # 爬取出错的用户
        self._step = 0  # 上一次持久化后添加的用户数，不需要关注并发，误差可以忽略
        self.running = False
        self._persisting = False  # 赋值操作具有原子性，可保线程安全，保证在persist时user_dict不被写入
        with open(kwargs.get('accounts_file', 'accounts.dat'), 'r') as f:
            accounts = [item.strip().split(':', 2) for item in f.read().split('\n') if item]
        if not accounts:
            raise Exception('must set accounts for spider')
        api_list = []
        workers = []  # 每个账户一个爬虫
        aliases = []
        for item in accounts:
            api = DoubanAPI(cfg={
                'logger': item[0],
                'persist_file': '__cache__' + item[0] + '.json',
            })
            time.sleep(1)
            if not api.user_alias:
                if len(item) > 2:
                    api.use(item[2])
                else:
                    api.login(item[0], item[1])
            if api.user_alias:
                aliases.append(item[0])
                api_list.append(api)
                workers.append(Worker(api, self))
        self.load()
        self._api = api_list[0]
        self._api.logger.info('spider start with accounts<%s>' % aliases)
        self._workers = workers
        self._sleep_workers = []
        self.init()
        atexit.register(self.abort)

    def abort(self):
        if not self.running:
            return
        self.running = False
        self._api.logger.info('spider aborted when parsing<%s>' % self._parsing)
        while self._parsing:
            self.reset_alias(self._parsing.pop())
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
        if not self.running or self._persisting or not user or user['alias'] in self._users_dict:
            return False
        user['parsed'] = False
        self._users_dict[user['alias']] = user
        if user['rev_contact_count'] > self._min_rev:
            self._users_list.append(user['alias'])
            self.wake_up()
        self._step += 1
        if self._step > self._persist_step:
            self.persist()
            self._step = 0
        return True

    def wake_up(self):
        if self._sleep_workers:
            self._sleep_workers.pop(0).start()

    def sleep(self, worker):
        self._workers.append(worker)

    def report(self, alias):
        if alias not in self._reports_dict:
            self._reports_dict[alias] = {
                'count': 1,
                'alias': alias,
                'url': API_PEOPLE_HOME % alias,
            }
        else:
            self._reports_dict[alias]['count'] += 1

    def has_alias(self, alias):
        """
        判断是否已爬取过用户
        
        :type alias: str
        :param alias: 
        
        :rtype: bool
        :return: 
        """
        return alias in self._users_dict or (alias in self._reports_dict and self._reports_dict[alias]['count'] > 2)

    def reset_alias(self, alias):
        if alias in self._users_dict:
            self._users_dict[alias]['parsed'] = False
            if alias not in self._users_list:
                self._users_list.append(alias)
        if alias in self._parsing:
            self._parsing.remove(alias)

    def next_alias(self):
        if not self._users_list:
            return None
        alias = self._users_list.pop(0)
        self._parsing.append(alias)
        return alias

    def done_alias(self, alias):
        if alias in self._users_dict:
            self._users_dict[alias]['parsed'] = True
        if alias in self._parsing:
            self._parsing.remove(alias)

    def init(self):
        for alias, user in self._users_dict.items():
            if user['rev_contact_count'] > self._min_rev and not user.get('parsed'):
                self._users_list.append(alias)
        for alias in self._init_users:
            if alias not in self._users_dict:
                try:
                    user = self._api.people.get_people(alias)
                    self.add_user(user)
                    time.sleep(2)
                except Exception as e:
                    self._api.logger.error('spider init user<%s> error: %s' % (alias, e))
        self._api.logger.debug('spider init with users<%s>, users to parse <%s>'
                               % (self._init_users, len(self._users_list)))

    def load(self):
        if os.path.isfile(self._persist_file):
            with open(self._persist_file, 'r') as f:
                data = json.load(f) or {}
                self._users_dict = data.get('users_dict', {})
                self._reports_dict = data.get('reports_dict', {})

    def persist(self):
        self._persisting = True
        with open(self._persist_file, 'w+') as f:
            self._api.logger.info('spider persist data, size: %s' % len(self._users_dict))
            json.dump({
                'users_dict': self._users_dict,
                'reports_dict': self._reports_dict,
            }, f, indent=2)
        with open(self._result_file, 'w+') as f:
            json.dump(self.summary(), f, indent=2)
        self._persisting = False

    def start(self):
        self.running = True
        [worker.start() for worker in self._workers]
        while True:
            time.sleep(1)

    def summary(self):
        total = len(self._users_dict)
        results = []
        for alias, user in self._users_dict.items():
            if user['rev_contact_count'] > self._min_rev:
                results.append(user)
        results.sort(key=lambda item: item['rev_contact_count'], reverse=True)
        return {'results': results, 'total': total, 'filtered': len(results)}


def test():
    spider = RelationSpider(**dict([arg.split('=', 1) for arg in argv[1:]]))
    spider.start()


if __name__ == '__main__':
    test()
