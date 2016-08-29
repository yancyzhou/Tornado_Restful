# -*- coding:utf-8 -*-
'''
======================
@author Vincent
======================
'''
# from __future__ import division
import tornado.web
import tornado.httpclient
import urllib2
import re
import textwrap
import json
import random
import math
import time
from tornado import gen
from urllib import unquote
from Handler import BaseHandler,TmpHandle
from Handler import VerifyIP
from bs4 import BeautifulSoup
from auth import jwtauth
from bson.objectid import ObjectId
import requests
import urllib

class VerificationUrl(BaseHandler):
    """检测url是否有效"""

    # @tornado.web.asynchronous
    @gen.coroutine
    def prepare(self):
        result = self.dbspy.rule.find({}).sort([("keywords",-1)])
        self.UrlRule = list(result)
        VerifyUrl = self.get_argument('url',None)
        data = []
        self._data = {}
        client = tornado.httpclient.AsyncHTTPClient()
        for item in self.UrlRule:
            FullUrl = VerifyUrl+item['rule']
            response = yield gen.Task(client.fetch, FullUrl)
            if item.has_key('keywords'):
                if len(item['keywords'])>0 and response.code == 200:
                    for keyword in item['keywords']:
                        if response.body.find(keyword.encode('utf-8'))!=-1:
                            data.append(item['rule'])
        self._data = {'data': data}

    # @gen.coroutine
    def POST(self):
        pass
