#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: Group.
import re
import traceback

from dbapi.BaseAPI import BaseAPI
from dbapi.endpoints import API_GROUP_SEARCH_GROUPS, API_GROUP_LIST_JOINED_GROUPS, API_GROUP_GROUP_HOME, \
    API_GROUP_SEARCH_TOPICS, API_GROUP_HOME, API_GROUP_LIST_GROUP_TOPICS, API_GROUP_LIST_USER_PUBLISHED_TOPICS, \
    API_GROUP_LIST_USER_COMMENTED_TOPICS, API_GROUP_LIST_USER_LIKED_TOPICS, API_GROUP_LIST_USER_RECED_TOPICS
from dbapi.utils import slash_right, build_list_result


def _parse_topic_table(xml, tds='title,created,comment,group', selector='//table[@class="olt"]//tr'):
    xml_results = xml.xpath(selector)
    results = []
    tds = tds.split(',')
    for item in xml_results:
        try:
            result = {}
            index = 0
            for td in tds:
                index += 1
                if td == 'title':
                    xml_title = item.xpath('.//td[position()=%s]/a' % index)[0]
                    url = xml_title.get('href')
                    tid = int(slash_right(url))
                    title = xml_title.text
                    result.update({'id': tid, 'url': url, 'title': title})
                elif td == 'created':
                    xml_created = item.xpath('.//td[position()=%s]/a' % index) \
                                  or item.xpath('.//td[position()=%s]' % index)
                    created_at = xml_created[0].get('title')
                    result['created_at'] = created_at
                elif td == 'comment':
                    xml_comment = item.xpath('.//td[position()=%s]/span' % index) \
                                  or item.xpath('.//td[position()=%s]' % index)
                    comment_count = int(re.match(r'\d+', xml_comment[0].text).group())
                    result['comment_count'] = comment_count
                elif td == 'group':
                    xml_group = item.xpath('.//td[position()=%s]/a' % index)[0]
                    group_url = xml_group.get('href')
                    group_alias = slash_right(group_url)
                    group_name = xml_group.text
                    result.update({'group_alias': group_alias, 'group_url': group_url, 'group_name': group_name})
                elif td == 'author':
                    xml_author = item.xpath('.//td[position()=%s]/a' % index)[0]
                    author_url = xml_author.get('href')
                    author_alias = slash_right(author_url)
                    author_nickname = xml_author.text
                    result.update({
                        'author_url': author_url,
                        'author_alias': author_alias,
                        'author_nickname': author_nickname,
                    })
                elif td == 'updated':
                    result['updated_at'] = item.xpath('.//td[position()=%s]/text()' % index)[0]
                elif td == 'time':
                    result['time'] = item.xpath('.//td[position()=%s]/text()' % index)[0]
                elif td == 'rec':
                    xml_rec = item.xpath('.//td[position()=%s]//a[@class="lnk-remove"]/@href' % (index - 1))[0]
                    result['rec_id'] = re.search(r'rec_id=(\d+)', xml_rec).groups()[0]
            results.append(result)
        except Exception as e:
            print('parse topic table exception: %s' % e, traceback.print_exc())
    return results


def _parse_total(xml):
    try:
        count = xml.xpath('//div[@class="paginator"]/span[@class="count"]/text()')[0]
        return int(re.search(r'\d+', count).group())
    except:
        return 0


class Group(BaseAPI):
    # 创建小组
    def add_group(self, **kwargs):
        raise NotImplementedError()

    # 搜索小组
    def search_groups(self, keyword, start=0):
        xml = self._xml(API_GROUP_SEARCH_GROUPS % (start, keyword))
        xml_results = xml.xpath('//div[@class="groups"]/div[@class="result"]')
        results = []
        for item in xml_results:
            try:
                url = item.xpath('.//h3/a/@href')[0]
                info = item.xpath('.//div[@class="content"]/div[@class="info"]/text()')[0].strip(' ')
                onclick = item.xpath('.//h3/a/@onclick')[0]
                meta = {
                    'icon': item.xpath('.//img/@src')[0],
                    'id': re.search(r'sid[^\d]+(\d+)', onclick).groups()[0],
                    'url': url,
                    'alias': url.rstrip('/').rsplit('/', 1)[1],
                    'name': item.xpath('.//h3/a/text()')[0],
                    'user_count': int(re.match(r'\d+', info).group()),
                    'user_alias': re.search(r'个(.+)\s*在此', info).groups()[0],
                }
                results.append(meta)
            except Exception as e:
                print('parse result error: %s' % e, traceback.print_exc())
        return build_list_result(results, _parse_total(xml))

    # 加入的小组列表，所有人
    def list_joined_groups(self, user_alias=None):
        xml = self._xml(API_GROUP_LIST_JOINED_GROUPS % (user_alias or self._user_alias))
        xml_results = xml.xpath('//div[@class="group-list group-cards"]/ul/li')
        results = []
        for item in xml_results:
            try:
                icon = item.xpath('.//img/@src')[0]
                link = item.xpath('.//div[@class="title"]/a')[0]
                url = link.get('href')
                name = link.text
                alias = url.rstrip('/').rsplit('/', 1)[1]
                user_count = int(item.xpath('.//span[@class="num"]/text()')[0][1:-1])
                results.append({
                    'icon': icon,
                    'alias': alias,
                    'url': url,
                    'name': name,
                    'user_count': user_count,
                })
            except Exception as e:
                print('list joined groups exception: %s' % e, traceback.print_exc())
        return build_list_result(results)

    # 删除小组
    def remove_group(self, group_id):
        raise NotImplementedError()

    # 加入小组
    def join_group(self, group_alias, message=None):
        xml = self._xml(API_GROUP_GROUP_HOME % group_alias, params={
            'action': 'join',
            'ck': self.ck(),
        })
        misc = xml.xpath('//div[@class="group-misc"]')[0]
        intro = misc.xpath('string(.)') or ''
        if intro.find('退出小组') > -1:
            return 'joined'
        elif intro.find('你已经申请加入小组') > -1:
            return 'waiting'
        elif intro.find('申请加入小组') > -1:
            res = self._xml(API_GROUP_GROUP_HOME % group_alias, 'post', data={
                'ck': self.ck(),
                'action': 'request_join',
                'message': message,
                'send': '发送',
            })
            misc = res.xpath('//div[@class="group-misc"]')[0]
            intro = misc.xpath('string(.)') or ''
            if intro.find('你已经申请加入小组') > -1:
                return 'waiting'
            else:
                return 'initial'
        else:
            return 'initial'

    # 离开小组
    def leave_group(self, group_alias):
        return self._xml(API_GROUP_GROUP_HOME % group_alias, params={
            'action': 'quit',
            'ck': self.ck(),
        })

    # 搜索话题
    def search_topics(self, keyword, sort='relevance', start=0):
        xml = self._xml(API_GROUP_SEARCH_TOPICS % (start, sort, keyword))
        return build_list_result(_parse_topic_table(xml), _parse_total(xml))

    # 小组内的话题，所有人
    def list_topics(self, group_alias, _type='', start=0):
        xml = self._xml(API_GROUP_LIST_GROUP_TOPICS % group_alias, params={
            'start': start,
            'type': _type,
        })
        return build_list_result(_parse_topic_table(xml, 'title,author,comment,updated'))

    # 已加入小组的所有话题，仅本人
    def list_joined_topics(self, start=0):
        xml = self._xml(API_GROUP_HOME, params={'start': start})
        return build_list_result(_parse_topic_table(xml, 'title,comment,created,group'), _parse_total(xml))

    # 发表的话题, 仅本人
    def list_user_topics(self, user_alias=None, start=0):
        user_alias = user_alias or self._user_alias
        xml = self._xml(API_GROUP_LIST_USER_PUBLISHED_TOPICS % user_alias, params={'start': start})
        return build_list_result(_parse_topic_table(xml, 'title,comment,created,group'), _parse_total(xml))

    # 回复过的话题列表，仅本人
    def list_commented_topics(self, start=0):
        xml = self._xml(API_GROUP_LIST_USER_COMMENTED_TOPICS % self._user_alias, params={'start': start})
        return build_list_result(_parse_topic_table(xml, 'title,comment,time,group'), _parse_total(xml))

    def list_liked_topics(self, user_alias=None, start=0):
        user_alias = user_alias or self._user_alias
        xml = self._xml(API_GROUP_LIST_USER_LIKED_TOPICS % user_alias, params={'start': start})
        return build_list_result(_parse_topic_table(xml, 'title,comment,time,group'), _parse_total(xml))

    # 推荐的话题列表
    def list_reced_topics(self, user_alias=None, start=0):
        user_alias = user_alias or self._user_alias
        xml = self._xml(API_GROUP_LIST_USER_RECED_TOPICS % user_alias, params={'start': start})
        return build_list_result(_parse_topic_table(xml, 'title,comment,time,group,rec'), _parse_total(xml))

    # 创建话题
    def add_topic(self, group_id, title, content):
        pass

    # 删除话题
    def remove_topic(self, topic_id):
        pass

    # 编辑话题
    def update_topic(self, topic_id, title, content):
        pass

    # 推荐话题
    def rec_topic(self, topic_id):
        pass

    # 喜欢话题
    def like_topic(self, topic_id):
        pass

    def undo_rec_topic(self, topic_id):
        pass

    def undo_like_topic(self, topic_id):
        pass

    # 回复列表
    def list_comments(self, topic_id, start=0):
        pass

    # 添加回复
    def add_comment(self, topic_id, content, reply_id):
        pass

    # 删除回复
    def remove_comment(self, comment_id):
        pass

    # 自己的回复
    def list_user_comments(self, topic_id, user_alias=None):
        pass
