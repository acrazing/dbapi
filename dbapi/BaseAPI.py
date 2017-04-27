#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: BaseAPI.
import requests
from lxml import html


class BaseAPI(object):
    def __init__(self, headers, cookies, user_alias):
        self._headers = headers or {}
        self._cookies = cookies or {}
        self._user_alias = user_alias or ''

    def ck(self):
        return self._cookies.get('ck', '')

    def _json(self, url, method='get', params=None, data=None):
        r = requests.request(method, url, params=params, data=data, cookies=self._cookies, headers=self._headers)
        return r.json()

    def _xml(self, url, method='get', params=None, data=None):
        print('[xml] %s: %s' % (method, url))
        r = requests.request(method, url, params=params, data=data, cookies=self._cookies, headers=self._headers)
        return html.fromstring(r.text, url)
