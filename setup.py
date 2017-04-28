#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: setup.
from setuptools import setup

setup(
    name='dbapi',
    version='0.0.1',
    description='基于爬虫的豆瓣API SDK',
    url='https://github.com/acrazing/dbapi',
    author='acrazing',
    author_email='joking.young@gmail.com',
    license='MIT',
    keywords='豆瓣 douban 豆瓣小组 api',
    install_requires=['lxml', 'requests'],
    packages=['dbapi'],
)
