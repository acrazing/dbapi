#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: setup.
from setuptools import setup

with open('./README.md', encoding='utf8') as f:
    desc = f.read()

with open('./requirements.txt') as f:
    requires = [r.split('=', 1)[0] for r in f.read().split('\n') if r]

setup(
    name='dbapi',
    version='0.0.11',
    description='基于爬虫的豆瓣API SDK',
    url='https://github.com/acrazing/dbapi',
    author='acrazing',
    author_email='joking.young@gmail.com',
    license='MIT',
    keywords='豆瓣 douban 豆瓣小组 api',
    long_description=desc,
    install_requires=requires,
    packages=['dbapi'],
    entry_points={
        'console_scripts': ['dbapi=dbapi.cli:main'],
    },
)
