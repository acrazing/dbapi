#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: DoubanAPI.
import os
import re
import sys
import time

import pickle
from pprint import pprint

import logging
import requests
from dbapi.Group import Group
from dbapi.config import api_config
from dbapi.endpoints import API_ACCOUNT_LOGIN, API_ACCOUNT_HOME, API_HOME, \
    API_ACCOUNT_LOGOUT
from dbapi.utils import slash_right


class DoubanAPI(object):
    """
    客户端入口类，提供各个模块接口及身份验证
    """

    def __init__(self, cfg=api_config):
        """
        :param cfg: 客户端配置
                persist_file: 用于持久化保存会话信息的文件
                headers: HTTP请求的公共头信息
        """
        self.headers = cfg.get('headers', api_config['headers'])
        self.persist_file = cfg.get('persist_file', api_config['persist_file'])
        self.cookies = {}
        self.username = ''
        self.password = ''
        self.user_alias = ''
        logger = logging.getLogger(cfg.get('logger', api_config['logger']))
        handler = logging.StreamHandler(cfg.get('log_destination', api_config['log_destination']))
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(cfg.get('log_level', api_config['log_level']))
        self.logger = logger
        self.load()  # 初始化时加载会话信息

    def persist(self):
        """
        持久化会话
        
        :return: self
        """
        with open(self.persist_file, 'wb+') as f:
            pickle.dump({
                'cookies': self.cookies,
                'username': self.username,
                'password': self.password,
                'user_alias': self.user_alias,
            }, f)
            self.logger.debug('persist session to <%s>' % self.persist_file)
        return self

    def load(self):
        """
        加载会话信息
        
        :return: self
        """
        if not os.path.isfile(self.persist_file):
            return self
        with open(self.persist_file, 'rb') as f:
            cfg = pickle.load(f) or {}
            self.cookies.update(cfg.get('cookies', {}))
            self.username = cfg.get('username', '')
            self.password = cfg.get('password', '')
            self.user_alias = cfg.get('user_alias', '')
            self.logger.debug('load session from <%s>' % self.persist_file)
        return self

    def login(self, username, password):
        """
        登录
        
        :param username: 用户名（手机号或者邮箱）
        :param password: 密码
        :return: self
        """
        r0 = requests.get(API_HOME, headers=self.headers)
        time.sleep(1)
        cookies = dict(r0.cookies)
        data = {
            'source': 'index_nav',
            'form_email': username,
            'form_password': password,
            'remember': 'on',
        }
        r1 = requests.post(API_ACCOUNT_LOGIN, headers=self.headers, cookies=cookies, data=data)
        cookies.update(dict(r1.cookies))
        [cookies.update(dict(r.cookies)) for r in r1.history]
        if 'dbcl2' not in cookies:
            raise Exception('Authorization failed: %s' % r1.url)
        cookies.update(dict(r1.cookies))
        self.username = username
        self.password = password
        self.logger.info('login with username <%s>' % self.username)
        self.use(cookies)
        return self

    def flush(self):
        """
        更新会话信息，主要是ck
        
        :return: self
        """
        r0 = requests.get(API_HOME, headers=self.headers, cookies=self.cookies)
        self.cookies.update(dict(r0.cookies))
        time.sleep(1)
        r1 = requests.get(API_ACCOUNT_HOME, headers=self.headers, cookies=self.cookies)
        self.user_alias = slash_right(r1.url)
        self.cookies.update(dict(r1.cookies))
        self.logger.log('flush with user_alias <%s>' % self.user_alias)
        return self

    def use(self, cookies):
        """
        如果遭遇验证码，用这个接口
        
        :param cookies: cookie字符串或者字典
        :return: self
        """
        self.cookies = dict([item.split('=', 1) for item in re.split(r'; *', cookies)]) \
            if isinstance(cookies, str) else cookies
        self.flush().persist()
        return self

    def logout(self):
        """
        登出会话
        
        :return: self
        """
        requests.get(API_ACCOUNT_LOGOUT % self.cookies.get('ck'), cookies=self.cookies)
        self.cookies = {}
        self.persist()
        return self

    @property
    def group(self):
        """
        豆瓣小组模块
        
        :return: dbapi.Group.Group
        """
        return Group(self.headers, self.cookies, self.user_alias, self.logger)


def test_api(argv):
    api = DoubanAPI()
    print('testing: %s.%s' % (argv[0], argv[1]))
    app = getattr(api, argv[0])
    func = getattr(app, argv[1])
    pprint(func(*argv[2:]))


def test_client(argv):
    api = DoubanAPI()
    print('testing: %s' % argv[0])
    func = getattr(api, argv[0])
    pprint(func(*argv[1:]))


if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2:])
