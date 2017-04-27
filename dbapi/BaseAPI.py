#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: BaseAPI.
import requests
from lxml import html


class BaseAPI(object):
    def __init__(self, headers, cookies):
        self._headers = headers
        self._cookies = cookies

    def _json(self, url, method='get', params=None, data=None):
        r = requests.request(method, url, params=params, data=data, cookies=self._cookies, headers=self._headers)
        return r.json()

    def _xml(self, url, method='get', params=None, data=None):
        r = requests.request(method, url, params=params, data=data, cookies=self._cookies, headers=self._headers)
        return html.fromstring(r.text, url)
