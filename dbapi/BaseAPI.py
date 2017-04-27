#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: BaseAPI.


class BaseAPI(object):
    def __init__(self, headers, cookies):
        self._headers = headers
        self._cookies = cookies

    def _request(self, url, method, payload):
        pass

    def _json(self, url, method, payload):
        pass

    def _xml(self, url, method, payload):
        pass
