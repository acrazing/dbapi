#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: config.
"""
默认配置
"""

import logging
import os
import sys

api_config = {
    'persist_file': os.path.join(os.path.expanduser("~"), ".__cache__dbapi.json"),
    'headers': {
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'zh,zh-CN;q=0.8,zh-TW;q=0.6,en;q=0.4,en-US;q=0.2',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/538.36 (KHTML, like Gecko) '
                      'Chrome/57.0.3029.110 Safari/538.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.douban.com/people/junbaoyang/',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    },
    'logger': 'dbapi',
    'log_level': logging.DEBUG,
    'log_destination': sys.stderr,
    'timeout': 5.0,
}
