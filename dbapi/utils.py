#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: utils.
import re


def slash_right(url='', index=1):
    return url.rstrip('/').rsplit('/', index)[index]


def build_list_result(results, xml):
    xml_count = xml.xpath('//div[@class="paginator"]/span[@class="count"]/text()')
    xml_next = xml.xpath('//div[@class="paginator"]/span[@class="next"]/a/@href')
    count = int(re.search(r'\d+', xml_count[0]).group()) if xml_count else len(results)
    next_start = int(re.search(r'start=(\d+)', xml_next[0]).groups()[0]) if xml_next else None
    return {'results': results, 'count': count, 'next_start': next_start}
