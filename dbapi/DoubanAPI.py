#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: DoubanAPI.
import json
import sys

from dbapi.Group import Group
from dbapi.People import People
from dbapi.base import BaseAPI


class DoubanAPI(BaseAPI):
    def __init__(self, **kwargs):
        super(DoubanAPI, self).__init__(**kwargs)

        self.group = Group(self)
        """:type: Group"""

        self.people = People(self)
        """:type: People"""


def default(data):
    try:
        return data.toJSON()
    except:
        try:
            return data.__repr__()
        except:
            try:
                return data.__class__.__name__
            except:
                return '__UNKNOWN__'


def test_api(argv):
    api = DoubanAPI()
    api.logger.info('testing: %s.%s' % (argv[0], argv[1]))
    app = getattr(api, argv[0])
    func = getattr(app, argv[1])
    print(json.dumps(func(*argv[2:]), indent=2, default=default))


def test_client(argv):
    api = DoubanAPI()
    api.logger.info('testing: %s' % argv[0])
    func = getattr(api, argv[0])
    print(json.dumps(func(*argv[1:]), indent=2, default=default))


if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2:])
