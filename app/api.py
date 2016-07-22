# -*- coding:utf-8 -*-
'''
======================
@author Vincent
======================
'''
from __future__ import division
import tornado.web
import tornado.httpclient
import urllib2
import re
import textwrap
import json
import random
import math
from tornado import gen
from urllib import unquote
from Handler import Handler
from Handler import VerifyIP
from bs4 import BeautifulSoup
from auth import jwtauth
from bson.objectid import ObjectId
import requests
import urllib


class VerificationUrl(Handler):
    """检测url是否有效"""
    def prepare(self):
        self.UrlRule = []
        for document in self.dbspy.resultcollection.find({'project': 'gethost', 'result.valid': 0}):
            for documentrule in self.dbspy.rule.find({}):
                if document['result']['url'][-1] == '/':
                    RuleUrl = document['result']['url']+documentrule['rule']
                else:
                    RuleUrl = document['result']['url']+'/'+documentrule['rule']
                self.UrlRule.append({'_id': document['_id'], 'cmsname': documentrule['host'], 'url': RuleUrl})

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        for item in self.UrlRule:
            self.httpExists(item)
        self.writejson({'data': 0})

    @tornado.web.asynchronous
    @gen.engine
    def httpExists(self, document):

        client = tornado.httpclient.AsyncHTTPClient()
        response = yield gen.Task(client.fetch, document['url'])
        if response.code == 200:
            result = self.dbspy.resultcollection.update({'_id': document['_id']}, {'$set': {'result.valid': 1, "cmsname": document['cmsname']}})
        else:
            result = self.dbspy.resultcollection.update({'_id': document['_id'], 'result.valid': 0}, {'$set': {'result.valid': -1}})
