#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: utils.
import re


def first(data, defaults=None):
    return data[0] if data else defaults


def slash_right(url='', index=1):
    """
    获取由/分割的字符串url的最后第index段，忽略结尾空串
    
    :param url: 字符串
    :param index: 第几个
    :return: str
    """
    return url.rstrip('/').rsplit('/', index)[1]


def build_list_result(results, xml):
    """
    构建带翻页的列表
    
    :param results: 已获取的数据列表
    :param xml: 原始页面xml
    :return: {'results': list, 'count': int, 'next_start': int|None}
            如果count与results长度不同，则有更多
            如果next_start不为None，则可以到下一页
    """
    xml_count = xml.xpath('//div[@class="paginator"]/span[@class="count"]/text()')
    xml_next = xml.xpath('//div[@class="paginator"]/span[@class="next"]/a/@href')
    count = int(re.search(r'\d+', xml_count[0]).group()) if xml_count else len(results)
    next_start = int(re.search(r'start=(\d+)', xml_next[0]).groups()[0]) if xml_next else None
    return {'results': results, 'count': count, 'next_start': next_start}
