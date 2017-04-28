#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: BaseAPI.
import requests
from lxml import html


class BaseAPI(object):
    """
    HTTP客户端封装
    """

    def __init__(self, headers, cookies, user_alias, logger):
        """
        初始化
        
        :param headers: 公共头
        :param cookies: 会话信息
        :param user_alias: 用户名
        :param logger: logging.Logger
        """
        self._headers = headers or {}
        self._cookies = cookies or {}
        self._user_alias = user_alias or ''
        self.logger = logger

    def ck(self):
        """
        获取ck
        
        :return: ck
        """
        return self._cookies.get('ck', '')

    def _req(self, url, method='get', params=None, data=None):
        """
        请求API
        
        :param url: API
        :param method: HTTP METHOD
        :param params: query
        :param data: body
        :return: Response
        """
        r = requests.request(method, url, params=params, data=data, cookies=self._cookies, headers=self._headers)
        self.logger.info('[api] %s: %s' % (method, r.url))
        return r

    def _json(self, url, method='get', params=None, data=None):
        """
        请求并返回json，参数同 _req()
        
        :param url: 
        :param method: 
        :param params: 
        :param data: 
        :return: 
        """
        r = self._req(url, method, params, data)
        return r.json()

    def _xml(self, url, method='get', params=None, data=None):
        """
        请求并返回xml，参数同 _req()
        
        :param url: 
        :param method: 
        :param params: 
        :param data: 
        :return: 
        """
        r = self._req(url, method, params, data)
        return html.fromstring(r.text, r.url)
