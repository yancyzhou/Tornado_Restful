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
from bs4 import BeautifulSoup
from auth import jwtauth
from bson.objectid import ObjectId
import requests
import urllib


class VerificationUrl(Handler):
    """检测url是否有效"""

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        UrlRule = self.get_argument('rule')
        import urllib
        n = self.dbs.resultcollection.find({'project': 'gethost', 'result.valid': 0}).limit(1000)
        for item in (yield n.to_list(1000)):
            # print self.getPR(item['result']['url'])
            if item['result']['url'][-1] == '/':
                Rule = item['result']['url']+UrlRule
            else:
                Rule = item['result']['url']+'/'+UrlRule
            self.httpExists(Rule)
        self.writejson({'data': 0})

    @tornado.web.asynchronous
    @gen.coroutine
    def httpExists(self, url):
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, url)

        self.code = response.code

        if self.code == 200:
            print url
        else:
            print str(self.code)+'     '+url

    GPR_HASH_SEED = "Mining PageRank is AGAINST GOOGLE'S TERMS OF SERVICE. Y\
    es, I'm talking to you, scammer."

    def google_hash(self, value):
        magic = 0x1020345
        for i in xrange(len(value)):
            magic ^= ord(self.GPR_HASH_SEED[i % len(self.GPR_HASH_SEED)]) ^ ord(value[i])
            magic = (magic >> 23 | magic << 9) & 0xFFFFFFFF
        return "8%08x" % (magic)

    def getPR(self, www):

        try:
            print self.google_hash(www)
            print www
            url = 'http://toolbarqueries.google.com.hk/tbr?client=navclient-auto&ch=%s&features=Rank&q=info:%s&gws_rd=cr' % (self.google_hash(www), www)
            print url
            response = requests.get(url)
            # print response
            rex = re.search(r'(.*?:.*?:)(\d+)', response.text)
            return rex.group(2)
        except:
            return None


# GetUrlAll
# @jwtauth
class GetUrlAll(Handler):
    """获取所有满足要求的url数据"""

    @gen.coroutine
    def get(self):
        self.keyword = self.get_argument('keywords')
        self.page = self.get_argument('currentpage', 1)
        self.pagesize = 20
        n = yield self.dbs.resultcollection.find({'project': 'gethost', 'result.valid': 0, 'result.url': {'$regex': self.keyword}}).count()
        res = self.dbs.resultcollection.find({'project': 'gethost', 'result.valid': 0, 'result.url': {'$regex': self.keyword}}).limit(self.pagesize).skip(self.pagesize*(int(self.page)-1))
        self.results = []
        for item in (yield res.to_list(20)):

            self.results.append(item['result'])

        self.writejson({'data': self.results, 'total': math.ceil(n/self.pagesize), 'currentpage': self.page})


# @jwtauth
class GetrRuleAll(Handler):
    """获取Rule"""
    @gen.coroutine
    def get(self):
        self.classname = self.get_argument('classname', None)
        self.host = self.get_argument('host', None)
        self.page = self.get_argument('currentpage', 1)
        self.pagesize = 10
        query = {}
        if self.classname is not None:
            query['classname'] = self.classname
        if self.host is not None:
            query['host'] = self.host
        n = yield self.dbs.rule.find(query).count()
        res = self.dbs.rule.find(query).limit(self.pagesize).skip(self.pagesize*(int(self.page)-1))
        self.results = []
        for item in (yield res.to_list(20)):
            item['_id'] = str(item["_id"])
            self.results.append(item)
        print self.results
        self.writejson({'data': self.results, 'total': math.ceil(n/self.pagesize), 'currentpage': self.page, 'code': 1})


# addrule
@jwtauth
class AddRule(Handler):
    """添加Url过滤规则"""

    @gen.coroutine
    def post(self):
        # print self.get_json_arguments(['rule','dshfkjsh','kjhdjkfsd'],**{'jskldjf':'asdas'})
        rule = self.get_json_argument('rules')
        host = self.get_json_argument('host')
        classname = self.get_json_argument('classname')
        print rule, host, classname
        obj = {}
        obj['rule'] = rule
        obj['host'] = host
        obj['classname'] = classname
        con = self.dbs.rule
        yield con.save(obj)
        print 'document _id: %s' % repr(obj['_id'])
        self.writejson({'data': repr(obj['_id']), 'code': 11, 'description': '添加成功！'})
