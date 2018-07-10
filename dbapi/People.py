#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 The Authors. All Rights Reserved.
# License: MIT.
# Author: acrazing <joking.young@gmail.com>.
# File: People.
import re

from dbapi.base import ModuleAPI
from dbapi.endpoints import API_PEOPLE_HOME, API_PEOPLE_LIST_CONTACTS, API_PEOPLE_LIST_USER_CONTACTS, \
    API_PEOPLE_LIST_REV_CONTACTS, API_PEOPLE_LIST_USER_REV_CONTACTS
from dbapi.utils import slash_right, build_list_result, first


class People(ModuleAPI):
    def get_people(self, user_alias=None):
        """
        获取用户信息
        
        :param user_alias: 用户ID
        :return: 
        """
        user_alias = user_alias or self.api.user_alias
        content = self.api.req(API_PEOPLE_HOME % user_alias).content
        xml = self.api.to_xml(re.sub(b'<br />', b'\n', content))
        try:
            xml_user = xml.xpath('//*[@id="profile"]')
            if not xml_user:
                return None
            else:
                xml_user = xml_user[0]
            avatar = first(xml_user.xpath('.//img/@src'))
            city = first(xml_user.xpath('.//div[@class="user-info"]/a/text()'))
            city_url = first(xml_user.xpath('.//div[@class="user-info"]/a/@href'))
            text_created_at = xml_user.xpath('.//div[@class="pl"]/text()')[1]
            created_at = re.match(r'.+(?=加入)', text_created_at.strip()).group()
            xml_intro = first(xml.xpath('//*[@id="intro_display"]'))
            intro = xml_intro.xpath('string(.)') if xml_intro is not None else None
            nickname = first(xml.xpath('//*[@id="db-usr-profile"]//h1/text()'), '').strip() or None
            signature = first(xml.xpath('//*[@id="display"]/text()'))
            xml_contact_count = xml.xpath('//*[@id="friend"]/h2')[0]
            contact_count = int(re.search(r'成员(\d+)', xml_contact_count.xpath('string(.)')).groups()[0])
            text_rev_contact_count = xml.xpath('//p[@class="rev-link"]/a/text()')[0]
            rev_contact_count = int(re.search(r'(\d+)人关注', text_rev_contact_count.strip()).groups()[0])
            return {
                'alias': user_alias,
                'url': API_PEOPLE_HOME % user_alias,
                'avatar': avatar,
                'city': city,
                'city_url': city_url,
                'created_at': created_at,
                'intro': intro,
                'nickname': nickname,
                'signature': signature,
                'contact_count': contact_count,
                'rev_contact_count': rev_contact_count,
            }
        except Exception as e:
            self.api.logger.exception('parse people meta error: %s' % e)

    def list_contacts(self, user_alias=None, start=0):
        results = []
        if user_alias is None:
            xml = self.api.xml(API_PEOPLE_LIST_CONTACTS, params={'start': start})
            for item in xml.xpath('//ul[@class="user-list"]/li'):
                try:
                    avatar = item.xpath('.//img/@src')[0]
                    nickname = item.xpath('.//img/@alt')[0]
                    url = item.xpath('.//a/@href')[0]
                    alias = slash_right(url)
                    city = item.xpath('.//span[@class="loc"]/text()')[0][3:]
                    signature = item.xpath('.//span[@class="signature"]/text()')[0][3:]
                    results.append({
                        'avatar': avatar,
                        'nickname': nickname,
                        'url': url,
                        'alias': alias,
                        'city': city,
                        'signature': signature,
                    })
                except Exception as e:
                    self.api.logger.exception('parse contact error: %s' % e)
        else:
            xml = self.api.xml(API_PEOPLE_LIST_USER_CONTACTS % user_alias, params={'start': start})
            for item in xml.xpath('//dl[@class="obu"]'):
                try:
                    avatar = item.xpath('.//img/@src')[0]
                    nickname = item.xpath('.//img/@alt')[0]
                    url = item.xpath('.//a/@href')[0]
                    alias = slash_right(url)
                    results.append({
                        'avatar': avatar,
                        'nickname': nickname,
                        'url': url,
                        'alias': alias,
                    })
                except Exception as e:
                    self.api.logger.exception('parse contact error: %s' % e)
        return build_list_result(results, xml)

    def list_rev_contacts(self, user_alias=None, start=0):
        results = []
        if user_alias is None:
            xml = self.api.xml(API_PEOPLE_LIST_REV_CONTACTS, params={'start': start})
            for item in xml.xpath('//ul[@class="user-list"]/li'):
                try:
                    avatar = item.xpath('.//img/@src')[0]
                    nickname = item.xpath('.//img/@alt')[0]
                    url = item.xpath('.//a/@href')[0]
                    alias = slash_right(url)
                    xml_info = item.xpath('.//div[@class="info"]/p')[0].xpath('string(.)').strip()
                    match = re.search(r'(.+)被[^\d]*(\d+).*关注[^\d]*(\d+)', xml_info, re.S)
                    city = None
                    contact_count = 0
                    rev_contact_count = 0
                    if match:
                        groups = match.groups()
                        city = groups[0].strip()
                        contact_count = int(groups[1].strip())
                        rev_contact_count = int(groups[2].strip())
                    results.append({
                        'avatar': avatar,
                        'nickname': nickname,
                        'url': url,
                        'alias': alias,
                        'city': city,
                        'contact_count': contact_count,
                        'rev_contact_count': rev_contact_count,
                    })
                except Exception as e:
                    self.api.logger.exception('parse rev contact list error: %s' % e)
        else:
            xml = self.api.xml(API_PEOPLE_LIST_USER_REV_CONTACTS % user_alias, params={'start': start})
            for item in xml.xpath('//dl[@class="obu"]'):
                try:
                    avatar = item.xpath('.//img/@src')[0]
                    nickname = item.xpath('.//img/@alt')[0]
                    url = item.xpath('.//a/@href')[0]
                    alias = slash_right(url)
                    results.append({
                        'avatar': avatar,
                        'nickname': nickname,
                        'url': url,
                        'alias': alias,
                    })
                except Exception as e:
                    self.api.logger.exception('parse rev contact list error: %s' % e)
        return build_list_result(results, xml)

    # 后面的接口先忽略，太多了……

    def list_statuses(self, user_alias=None, start=0):
        pass

    def list_status_comments(self, user_alias=None, start=0):
        pass

    def like_status(self, status_id):
        pass

    def undo_like_status(self, status_id):
        pass

    def add_status(self, **kwargs):
        pass

    def remove_status(self, status_id):
        pass

    def list_albums(self, user_alias=None):
        pass

    def add_album(self, **kwargs):
        pass

    def update_album(self, **kwargs):
        pass

    def remove_album(self, album_id):
        pass

    def get_album(self, album_id):
        pass

    def add_album_comment(self, **kwargs):
        pass

    def remove_album_comment(self, **kwargs):
        pass

    def list_photos(self, album_id):
        pass

    def get_photo(self, photo_id):
        pass

    def add_photo(self, **kwargs):
        pass

    def remove_photo(self, photo_id):
        pass

    def like_photo(self, photo_id):
        pass

    def rec_photo(self, photo_id):
        pass

    def undo_like_photo(self, photo_id):
        pass

    def undo_rec_photo(self, photo_id):
        pass

    def list_photo_comments(self, photo_id, start=0):
        pass

    def add_photo_comment(self, photo_id, content):
        pass

    def remove_photo_comment(self, comment_id):
        pass

    def list_photo_recs(self, photo_id, start=0):
        pass

    def list_photo_likes(self, photo_id, start=0):
        pass
