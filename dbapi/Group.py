#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: Group.
"""
豆瓣小组相关API
"""
import re
from html import unescape

from lxml import etree

from dbapi.base import ModuleAPI
from dbapi.endpoints import API_GROUP_SEARCH_GROUPS, API_GROUP_LIST_JOINED_GROUPS, API_GROUP_GROUP_HOME, \
    API_GROUP_SEARCH_TOPICS, API_GROUP_HOME, API_GROUP_LIST_GROUP_TOPICS, API_GROUP_LIST_USER_PUBLISHED_TOPICS, \
    API_GROUP_LIST_USER_COMMENTED_TOPICS, API_GROUP_LIST_USER_LIKED_TOPICS, API_GROUP_LIST_USER_RECED_TOPICS, \
    API_GROUP_ADD_TOPIC, API_GROUP_REMOVE_COMMENT, API_GROUP_GET_TOPIC, \
    API_GROUP_REMOVE_TOPIC, API_GROUP_UPDATE_TOPIC, API_GROUP_ADD_COMMENT, API_GROUP_ADMIN_REMOVE_COMMENT
from dbapi.utils import slash_right, build_list_result


class Group(ModuleAPI):
    """
    豆瓣小组客户端
    """

    def _parse_topic_table(self, xml, tds='title,created,comment,group', selector='//table[@class="olt"]//tr'):
        """
        解析话题列表
        
        :internal
        :param xml: 页面XML 
        :param tds: 每列的含义，可以是title, created, comment, group, updated, author, time, rec
        :param selector: 表在页面中的位置
        :return: 
        """
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
                self.api.api.logger.exception('parse topic table exception: %s' % e)
        return results

    def add_group(self, **kwargs):
        """
        创建小组
        
        :param kwargs: 
        :return: 
        """
        raise NotImplementedError()

    def search_groups(self, keyword, start=0):
        """
        搜索小组
        
        :param keyword: 搜索的关键字
        :param start: 翻页
        :return: 含总数的列表
        """
        xml = self.api.xml(API_GROUP_SEARCH_GROUPS % (start, keyword))
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
                self.api.logger.exception('parse search groups result error: %s' % e)
        return build_list_result(results, xml)

    def list_joined_groups(self, user_alias=None):
        """
        已加入的小组列表
        
        :param user_alias: 用户名，默认为当前用户名
        :return: 单页列表
        """
        xml = self.api.xml(API_GROUP_LIST_JOINED_GROUPS % (user_alias or self.api.user_alias))
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
                self.api.logger.exception('parse joined groups exception: %s' % e)
        return build_list_result(results, xml)

    def remove_group(self, group_id):
        """
        删除小组
        
        :param group_id: 小组ID
        :return: 
        """
        raise NotImplementedError()

    def join_group(self, group_alias, message=None):
        """
        加入小组
        
        :param group_alias: 小组ID
        :param message: 如果要验证，留言信息
        :return: 枚举
                - joined: 加入成功
                - waiting: 等待审核
                - initial: 加入失败
        """
        xml = self.api.xml(API_GROUP_GROUP_HOME % group_alias, params={
            'action': 'join',
            'ck': self.api.ck(),
        })
        misc = xml.xpath('//div[@class="group-misc"]')[0]
        intro = misc.xpath('string(.)') or ''
        if intro.find('退出小组') > -1:
            return 'joined'
        elif intro.find('你已经申请加入小组') > -1:
            return 'waiting'
        elif intro.find('申请加入小组') > -1:
            res = self.api.xml(API_GROUP_GROUP_HOME % group_alias, 'post', data={
                'ck': self.api.ck(),
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

    def leave_group(self, group_alias):
        """
        退出小组
        
        :param group_alias: 小组ID
        :return: 
        """
        return self.api.req(API_GROUP_GROUP_HOME % group_alias, params={
            'action': 'quit',
            'ck': self.api.ck(),
        })

    def search_topics(self, keyword, sort='relevance', start=0):
        """
        搜索话题
        
        :param keyword: 关键字
        :param sort: 排序方式 relevance/newest
        :param start: 翻页
        :return: 带总数的列表
        """
        xml = self.api.xml(API_GROUP_SEARCH_TOPICS % (start, sort, keyword))
        return build_list_result(self._parse_topic_table(xml), xml)

    def list_topics(self, group_alias, _type='', start=0):
        """
        小组内话题列表
        
        :param group_alias: 小组ID
        :param _type: 类型 默认最新，hot:最热
        :param start: 翻页
        :return: 带下一页的列表
        """
        xml = self.api.xml(API_GROUP_LIST_GROUP_TOPICS % group_alias, params={
            'start': start,
            'type': _type,
        })
        return build_list_result(self._parse_topic_table(xml, 'title,author,comment,updated'), xml)

    def list_joined_topics(self, start=0):
        """
        已加入的所有小组的话题列表
        
        :param start: 翻页
        :return: 带下一页的列表
        """
        xml = self.api.xml(API_GROUP_HOME, params={'start': start})
        return build_list_result(self._parse_topic_table(xml, 'title,comment,created,group'), xml)

    def list_user_topics(self, start=0):
        """
        发表的话题
        
        :param start: 翻页
        :return: 带下一页的列表
        """
        xml = self.api.xml(API_GROUP_LIST_USER_PUBLISHED_TOPICS % self.api.user_alias, params={'start': start})
        return build_list_result(self._parse_topic_table(xml, 'title,comment,created,group'), xml)

    def list_commented_topics(self, start=0):
        """
        回复过的话题列表
        
        :param start: 翻页
        :return: 带下一页的列表
        """
        xml = self.api.xml(API_GROUP_LIST_USER_COMMENTED_TOPICS % self.api.user_alias, params={'start': start})
        return build_list_result(self._parse_topic_table(xml, 'title,comment,time,group'), xml)

    def list_liked_topics(self, user_alias=None, start=0):
        """
        喜欢过的话题
        
        :param user_alias: 指定用户，默认当前
        :param start: 翻页
        :return: 带下一页的列表
        """
        user_alias = user_alias or self.api.user_alias
        xml = self.api.xml(API_GROUP_LIST_USER_LIKED_TOPICS % user_alias, params={'start': start})
        return build_list_result(self._parse_topic_table(xml, 'title,comment,time,group'), xml)

    def list_reced_topics(self, user_alias=None, start=0):
        """
        推荐的话题列表
        
        :param user_alias: 指定用户，默认当前
        :param start: 翻页
        :return: 带下一页的列表
        """
        user_alias = user_alias or self.api.user_alias
        xml = self.api.xml(API_GROUP_LIST_USER_RECED_TOPICS % user_alias, params={'start': start})
        return build_list_result(self._parse_topic_table(xml, 'title,comment,time,group,rec'), xml)

    def add_topic(self, group_alias, title, content):
        """
        创建话题（小心验证码~）
        
        :param group_alias: 小组ID
        :param title: 标题
        :param content: 内容
        :return: bool
        """
        xml = self.api.req(API_GROUP_ADD_TOPIC % group_alias, 'post', data={
            'ck': self.api.ck(),
            'rev_title': title,
            'rev_text': content,
            'rev_submit': '好了，发言',
        })
        return not xml.url.startswith(API_GROUP_ADD_TOPIC % group_alias)

    def get_topic(self, topic_id):
        xml = self.api.xml(API_GROUP_GET_TOPIC % topic_id)
        txt_title = xml.xpath('//div[@id="content"]/h1/text()')[0].strip()
        txt_content = xml.xpath('//div[@class="topic-content"]')[0].xpath('string()').strip()
        txt_author_avatar = xml.xpath('//img[@class="pil"]/@src')[0]
        xml_from = xml.xpath('//div[@class="topic-doc"]//span[@class="from"]/a')[0]
        txt_created_at = xml.xpath('//div[@class="topic-doc"]//span[@class="color-green"]/text()')[0]
        xml_group = xml.xpath('//div[@id="g-side-info-member"]')[0]
        txt_group_avatar = xml_group.xpath('.//img/@src')[0]
        xml_group_title = xml_group.xpath('.//div[@class="title"]/a')[0]
        txt_author_url = xml_from.get('href')
        txt_group_url = xml_group_title.get('href').split('?', 1)[0]
        return {
            'id': topic_id,
            'title': txt_title,
            'content': txt_content,
            'created_at': txt_created_at,
            'author_avatar': txt_author_avatar,
            'author_nickname': xml_from.text,
            'author_alias': slash_right(txt_author_url),
            'author_url': txt_author_url,
            'group_icon': txt_group_avatar,
            'group_name': xml_group.xpath('.//div[@class="title"]/a/text()')[0],
            'group_alias': slash_right(txt_group_url),
            'group_url': txt_group_url,
        }

    def remove_topic(self, topic_id):
        """
        删除话题（需要先删除所有评论，使用默认参数）
        
        :param topic_id: 话题ID
        :return: None
        """
        comment_start = 0
        while comment_start is not None:
            comments = self.list_comments(topic_id, comment_start)
            for comment in comments['results']:
                self.remove_comment(topic_id, comment['id'])
            comment_start = comments['next_start']
        return self.api.req(API_GROUP_REMOVE_TOPIC % topic_id, params={'ck': self.api.ck()})

    def update_topic(self, topic_id, title, content):
        """
        更新话题
        
        :param topic_id: 话题ID
        :param title: 标题
        :param content: 内容
        :return: bool
        """
        xml = self.api.req(API_GROUP_UPDATE_TOPIC % topic_id, 'post', data={
            'ck': self.api.ck(),
            'rev_title': title,
            'rev_text': content,
            'rev_submit': '好了，改吧',
        })
        return not xml.url.startswith(API_GROUP_UPDATE_TOPIC % topic_id)

    def rec_topic(self, topic_id):
        """
        推荐话题
        
        :param topic_id: 话题ID
        :return: 
        """
        raise NotImplementedError('Too complex')

    def like_topic(self, topic_id):
        """
        喜欢话题
        
        :param topic_id: 话题ID
        :return: 
        """
        raise NotImplementedError('Too complex')

    def undo_rec_topic(self, rec_id):
        """
        取消推荐
        
        :param rec_id: 推荐ID
        :return: 
        """
        raise NotImplementedError('Too complex')

    def undo_like_topic(self, topic_id):
        """
        取消喜欢
        
        :param topic_id: 话题ID
        :return: 
        """
        raise NotImplementedError('Too complex')

    def list_comments(self, topic_id, start=0):
        """
        回复列表
        
        :param topic_id: 话题ID
        :param start: 翻页
        :return: 带下一页的列表
        """
        xml = self.api.xml(API_GROUP_GET_TOPIC % topic_id, params={'start': start})
        xml_results = xml.xpath('//ul[@id="comments"]/li')
        results = []
        for item in xml_results:
            try:
                author_avatar = item.xpath('.//img/@src')[0]
                author_url = item.xpath('.//div[@class="user-face"]/a/@href')[0]
                author_alias = slash_right(author_url)
                author_signature = item.xpath('.//h4/text()')[1].strip()
                author_nickname = item.xpath('.//h4/a/text()')[0].strip()
                created_at = item.xpath('.//h4/span/text()')[0].strip()
                content = etree.tostring(item.xpath('.//div[@class="reply-doc content"]/p')[0]).decode('utf8').strip()
                cid = item.get('id')
                results.append({
                    'id': cid,
                    'author_avatar': author_avatar,
                    'author_url': author_url,
                    'author_alias': author_alias,
                    'author_signature': author_signature,
                    'author_nickname': author_nickname,
                    'created_at': created_at,
                    'content': unescape(content),
                })
            except Exception as e:
                self.api.logger.exception('parse comment exception: %s' % e)
        return build_list_result(results, xml)

    def add_comment(self, topic_id, content, reply_id=None):
        """
        添加评论
        
        :param topic_id: 话题ID
        :param content: 内容
        :param reply_id: 回复ID
        :return: None
        """
        return self.api.req(API_GROUP_ADD_COMMENT % topic_id, 'post', data={
            'ck': self.api.ck(),
            'ref_cid': reply_id,
            'rv_comment': content,
            'start': 0,
            'submit_btn': '加上去',
        })

    def remove_comment(self, topic_id, comment_id, reason='0', other=None):
        """
        删除评论（自己发的话题所有的都可以删除，否则只能删自己发的）
        
        :param topic_id: 话题ID
        :param comment_id: 评论ID
        :param reason: 原因 0/1/2 （内容不符/反动/其它）
        :param other: 其它原因的具体(2)
        :return: None
        """
        params = {'cid': comment_id}
        data = {'cid': comment_id, 'ck': self.api.ck(), 'reason': reason, 'other': other, 'submit': '确定'}
        r = self.api.req(API_GROUP_REMOVE_COMMENT % topic_id, 'post', params, data)
        if r.text.find('douban_admin') > -1:
            r = self.api.req(API_GROUP_ADMIN_REMOVE_COMMENT % topic_id, 'post', params, data)
        self.api.logger.debug('remove comment final url is <%s>' % r.url)
        return r

    def list_user_comments(self, topic_id, user_alias=None):
        """
        列出用户在话题下的所有回复
        
        :param topic_id: 话题ID
        :param user_alias: 用户ID，默认当前
        :return: 纯列表
        """
        user_alias = user_alias or self.api.user_alias
        comment_start = 0
        results = []
        while comment_start is not None:
            comments = self.list_comments(topic_id, comment_start)
            results += [item for item in comments['results'] if item['author_alias'] == user_alias]
            comment_start = comments['next_start']
        return results

    def remove_commented_topic(self, topic_id):
        """
        删除回复的话题（删除所有自己发布的评论）
        
        :param topic_id: 话题ID
        :return: None
        """
        return [self.remove_comment(topic_id, item['id']) for item in self.list_user_comments(topic_id)]
