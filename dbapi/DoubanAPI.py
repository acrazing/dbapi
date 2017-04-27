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
from pprint import pprint

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
