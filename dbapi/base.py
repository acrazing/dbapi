#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: BaseAPI.
import json
import logging
import os
import re
import time

import requests
from lxml import html

from dbapi.config import api_config
from dbapi.endpoints import API_ACCOUNT_HOME, API_HOME, API_ACCOUNT_LOGIN, API_ACCOUNT_LOGOUT
from dbapi.utils import slash_right

RE_SESSION_EXPIRE = re.compile(r'sec\.douban\.com|douban\.com/accounts/login|douban\.com/mine/')


class BaseAPI(object):
    """
    客户端入口类，提供各个模块接口及身份验证
    """

    def __init__(self, flush=True, **kwargs):
        """
        :param flush:
        :param kwargs: 客户端配置
                persist_file: 用于持久化保存会话信息的文件
                headers: HTTP请求的公共头信息
                logger: Logger的名称
                log_destination: 输出
                log_level: 等级
                timeout: 接口请求超时
        """
        self.headers = kwargs.get('headers', api_config['headers'])
        """:type: dict"""

        self.persist_file = kwargs.get('persist_file', api_config['persist_file'])
        """:type: str"""

        self.timeout = kwargs.get('timeout', api_config['timeout'])
        """:type: float"""

        self.cookies = {}
        """
        :type: dict
        
        Must not be None
        """

        self.user_alias = None
        """:type: str"""

        logger = logging.getLogger(kwargs.get('logger', api_config['logger']))
        if len(logger.handlers) is 0:
            handler = logging.StreamHandler(kwargs.get('log_destination', api_config['log_destination']))
            formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(kwargs.get('log_level', api_config['log_level']))
        self.logger = logger
        """:type: logging.Logger"""

        self.load()  # 初始化时加载会话信息
        flush is True and self.flush()

    def req(self, url, method='get', params=None, data=None, auth=False):
        """
        请求API

        :type url: str
        :param url: API
        
        :type method: str
        :param method: HTTP METHOD
        
        :type params: dict
        :param params: query
        
        :type data: dict
        :param data: body
        
        :type auth: bool
        :param auth: if True and session expired will raise exception
        
        :rtype: requests.Response
        :return: Response
        """
        self.logger.debug('fetch api<%s:%s>' % (method, url))
        if auth and self.user_alias is None:
            raise Exception('cannot fetch api<%s> without session' % url)
        s = requests.Session()
        r = s.request(method, url, params=params, data=data, cookies=self.cookies, headers=self.headers,
                      timeout=self.timeout)
        s.close()
        if r.url is not url and RE_SESSION_EXPIRE.search(r.url) is not None:
            self.expire()
            if auth:
                raise Exception('auth expired, could not fetch with<%s>' % url)
        return r

    def json(self, url, method='get', params=None, data=None):
        """
        请求并返回json
        
        
        :type url: str
        :param url: API
        
        :type method: str
        :param method: HTTP METHOD
        
        :type params: dict
        :param params: query
        
        :type data: dict
        :param data: body
        
        :rtype: dict
        :return: 
        """
        r = self.req(url, method, params, data)
        return r.json()

    @staticmethod
    def to_xml(content, **kwargs):
        return html.fromstring(html=content, parser=html.HTMLParser(encoding='utf-8'), **kwargs)

    def xml(self, url, method='get', params=None, data=None):
        """
        请求并返回xml
        
        :type url: str
        :param url: API
        
        :type method: str
        :param method: HTTP METHOD
        
        :type params: dict
        :param params: query
        
        :type data: dict
        :param data: body
        
        :rtype: html.HtmlElement
        :return: 
        """
        r = self.req(url, method, params, data)
        # this is required for avoid utf8-mb4 lead to encoding error
        return self.to_xml(r.content, base_url=r.url)

    def persist(self):
        """
        持久化会话信息
        """
        with open(self.persist_file, 'w+') as f:
            json.dump({
                'cookies': self.cookies,
                'user_alias': self.user_alias,
            }, f, indent=2)
            self.logger.debug('persist session to <%s>' % self.persist_file)

    def load(self):
        """
        加载会话信息
        """
        if not os.path.isfile(self.persist_file):
            return
        with open(self.persist_file, 'r') as f:
            cfg = json.load(f) or {}
            self.cookies = cfg.get('cookies', {})
            self.user_alias = cfg.get('user_alias') or None
            self.logger.debug('load session for <%s> from <%s>' % (self.user_alias, self.persist_file))

    def expire(self):
        if self.user_alias is None:
            return
        self.logger.warning('session expired for <%s>' % self.user_alias)
        self.cookies = {}
        self.user_alias = None
        self.persist()

    def flush(self):
        """
        更新会话信息，主要是ck, user_alias
        """
        if 'dbcl2' not in self.cookies:
            return
        r = self.req(API_ACCOUNT_HOME)
        if RE_SESSION_EXPIRE.search(r.url):
            return self.expire()
        self.cookies.update(dict(r.cookies))
        self.user_alias = slash_right(r.url)
        self.logger.debug('flush with user_alias <%s>' % self.user_alias)
        return

    def login(self, username, password):
        """
        登录
        
        :type username: str
        :param username: 用户名（手机号或者邮箱）
        
        :type password: str
        :param password: 密码
        """
        r0 = self.req(API_HOME)
        time.sleep(1)
        cookies = dict(r0.cookies)
        data = {
            'source': 'index_nav',
            'form_email': username,
            'form_password': password,
            'remember': 'on',
        }
        r1 = self.req(API_ACCOUNT_LOGIN, method='post', data=data)
        cookies.update(dict(r1.cookies))
        [cookies.update(dict(r.cookies)) for r in r1.history]
        if 'dbcl2' not in cookies:
            raise Exception('Authorization failed for <%s>: %s' % (username, r1.url))
        cookies.update(dict(r1.cookies))
        self.logger.info('login with username <%s>' % username)
        self.use(cookies)
        return self

    def use(self, cookies):
        """
        如果遭遇验证码，用这个接口
        
        :type cookies: str|dict
        :param cookies: cookie字符串或者字典
        :return: self
        """
        self.cookies = dict([item.split('=', 1) for item in re.split(r'; *', cookies)]) \
            if isinstance(cookies, str) else cookies
        self.flush()
        self.persist()
        return self

    def logout(self):
        """
        登出会话
        
        :return: self
        """
        self.req(API_ACCOUNT_LOGOUT % self.ck())
        self.cookies = {}
        self.user_alias = None
        self.persist()

    def ck(self):
        """
        获取ck
        
        :rtype: str
        :return: ck
        """
        return self.cookies.get('ck', '')

    def toJSON(self):
        return 'douban client <%s> for <%s>' % (self.__class__.__name__, self.user_alias)


class ModuleAPI:
    def __init__(self, api):
        """
        :type api: BaseAPI
        :param api: 
        """
        self.api = api

    def toJSON(self):
        return 'douban module <%s>' % self.__class__.__name__
