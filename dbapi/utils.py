#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: utils.


def slash_right(url='', index=1):
    return url.rstrip('/').rsplit('/', index)[index]


def build_list_result(results=[], total=0):
    return {'results': results, 'total': total or len(results)}
