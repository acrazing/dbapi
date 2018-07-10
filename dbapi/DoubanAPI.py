#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: DoubanAPI.

from dbapi.Group import Group
from dbapi.People import People
from dbapi.base import BaseAPI


class DoubanAPI(BaseAPI):
    def __init__(self, flush=True, **kwargs):
        super(DoubanAPI, self).__init__(flush=flush, **kwargs)

        self.group = Group(self)
        """:type: Group"""

        self.people = People(self)
        """:type: People"""
