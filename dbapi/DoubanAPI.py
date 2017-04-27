#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: DoubanAPI.
import os
import sys
import time

import pickle
import requests
from dbapi.Group import Group
from dbapi.config import api_config
from dbapi.endpoints import API_ACCOUNT_LOGIN, API_ACCOUNT_HOME, API_HOME, \
    API_ACCOUNT_LOGOUT


class DoubanAPI(object):
    def __init__(self, config=api_config):
        self.config = config
        self.cookies = config.get('cookies', {})
        self.headers = config.get('headers', {})
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.user_alias = config.get('user_alias', '')
        self.persist_file = config.get('persist_file', '__cache__.dat')
        self.load()

    def persist(self):
        with open(self.persist_file, 'wb+') as f:
            pickle.dump({
                'cookies': self.cookies,
                'username': self.username,
                'password': self.password,
                'user_alias': self.user_alias,
            }, f)
        return self

    def load(self):
        if not os.path.isfile(self.persist_file):
            return self
        with open(self.persist_file, 'rb') as f:
            config = pickle.load(f) or {}
            self.cookies.update(config.get('cookies', {}))
            self.username = config.get('username', '')
            self.password = config.get('password', '')
            self.user_alias = config.get('user_alias', '')
        return self

    def login(self, username, password):
        r0 = requests.get(API_HOME, headers=self.headers)
        time.sleep(1)
        cookies = dict(r0.cookies)
        data = {
            'source': 'index_nav',
            'form_email': username,
            'form_password': password,
            'remember': 'on',
        }
        r1 = requests.post(API_ACCOUNT_LOGIN, headers=self.headers, cookies=cookies, data=data, allow_redirects=False)
        if not r1.headers.get('Location', '').startswith(API_HOME):
            raise Exception('Authorization failed: %s' % r1.headers.get('Location'))
        cookies.update(dict(r1.cookies))
        self.username = username
        self.password = password
        self.use(cookies)
        return self

    def flush(self):
        r0 = requests.get(API_HOME, headers=self.headers, cookies=self.cookies)
        self.cookies.update(dict(r0.cookies))
        time.sleep(1)
        r1 = requests.get(API_ACCOUNT_HOME, headers=self.headers, cookies=self.cookies)
        self.user_alias = r1.url.rstrip('/').rsplit('/', 1)[1]
        self.cookies.update(dict(r1.cookies))
        return self

    def use(self, cookies):
        self.cookies = cookies
        self.flush().persist()
        return self

    def logout(self):
        requests.get(API_ACCOUNT_LOGOUT % self.cookies.get('ck'), cookies=self.cookies)
        self.cookies = {}
        self.persist()
        return self

    @property
    def group(self):
        return Group(self.headers, self.cookies, self.user_alias)


def test_login(argv):
    api = DoubanAPI()
    api.login(argv[0], argv[1])
    print('login with username: %s, password: %s' % (api.username, api.password))
    print('user home url: %s' % api.user_alias)
    print('cookies', api.cookies)


def test_persist(argv):
    api = DoubanAPI()
    cookies = {}
    [cookies.update((c.split('=', 1),)) for c in argv[0].split('; ')]
    api.use(cookies)
    print('used: alias: %s' % api.user_alias)
    api2 = DoubanAPI()
    print('load cookies', api2.cookies)
    r2 = requests.get(API_ACCOUNT_HOME, cookies=api2.cookies, headers=api2.headers)
    print('load result: %s' % r2.url)


def test_argv(argv):
    origin = "ll=\"108296\"; bid=78vrfvr1mMU; _ga=GA1.2.897983712.1493266936; ap=1; " \
             "_vwo_uuid_v2=47B9B09B65CC50A3B87593B27E72A38F|0e509048565e477027bd2f7b15eeebd1; " \
             "__utma=30149280.897983712.1493266936.1493266936.1493266936.1; __utmb=30149280.11.10.1493266936; " \
             "__utmz=30149280.1493266936.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=30149280.6101; " \
             "ck=fLns; _pk_id.100001.8cb4=75ccca2b64c8e7b4.1493266929.1.1493272150.1493266929.; " \
             "_pk_ses.100001.8cb4=*; push_noty_num=0; push_doumail_num=0 "
    arg = argv[0]
    print('equals:', arg == origin)
    r1 = requests.get(API_ACCOUNT_HOME, headers={'Cookie': arg})
    print('r1.url:', r1.url)
    r2 = requests.get(API_ACCOUNT_HOME, headers={'Cookie': origin})
    print('r2.url:', r2.url)


def test_first_api(argv):
    api = DoubanAPI()
    print('searched groups:', api.group.search_groups('group'))


def test_api(argv):
    api = DoubanAPI()
    print('testing: %s.%s' % (argv[0], argv[1]))
    app = getattr(api, argv[0])
    func = getattr(app, argv[1])
    print('result:', func(*argv[2:]))


if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2:])
