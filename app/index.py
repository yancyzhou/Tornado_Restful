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
from Handler import BaseHandler,TmpHandle
from Handler import VerifyIP
from bs4 import BeautifulSoup
from auth import jwtauth
from bson.objectid import ObjectId
import requests
import urllib


# @jwtauth
@VerifyIP
class GetUrlAll(BaseHandler):
    """获取所有满足要求的url数据"""

    @gen.coroutine
    def prepare(self):
        self.keyword = self.get_argument('keywords')
        self.page = self.get_argument('currentpage', 1)
        self.pagesize = 20
        n = yield self.dbs.resultcollection.find({'project': 'gethost', 'result.valid': -1, 'result.url': {'$regex': self.keyword}}).count()
        res = self.dbs.resultcollection.find({'project': 'gethost', 'result.valid': -1, 'result.url': {'$regex': self.keyword}}).limit(self.pagesize).skip(self.pagesize*(int(self.page)-1))
        self.results = []
        for item in (yield res.to_list(20)):

            self.results.append(item['result'])
        self._data = {'data': self.results, 'total': math.ceil(n/self.pagesize), 'currentpage': self.page}
    def GET(self):
        pass


# @jwtauth
class GetrRuleAll(BaseHandler):
    """获取Rule"""

    @gen.coroutine
    def prepare(self):
        # print dir(self)
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

        self._data = {'data': self.results, 'total': math.ceil(n/self.pagesize), 'currentpage': self.page, 'code': 1}
        #self.writejson({'data': self.results, 'total': math.ceil(n/self.pagesize), 'currentpage': self.page})
    def GET(self):
        pass

# addrule
@jwtauth
class AddRule(BaseHandler):
    """添加Url过滤规则"""

    @gen.coroutine
    def post(self):
        rule = self.get_json_argument('rule')
        host = self.get_json_argument('host')
        # classname = self.get_json_argument('classname')
        if rule and host:
            obj = {}
            obj['rule'] = rule
            obj['host'] = host
            # obj['classname'] = classname
            con = self.dbs.rule
            yield con.save(obj)
            self.writejson({'data': repr(obj['_id']), 'code': 1, 'description': '添加成功！'})


class DelRule(BaseHandler):

    @gen.coroutine
    def post(self):
        id = self.get_json_argument('ruleid')
        if id:
            obj = {}
            obj['_id'] = ObjectId(id)
            con = self.dbs.rule
            yield con.remove(obj)
            self.writejson({'data': repr(obj['_id']), 'code': 1, 'description': '删除成功！'})

class getshodan(BaseHandler):
    @gen.coroutine
    def prepare(self):
        import shodan

        iplist = []
        total = 0
        SHODAN_API_KEY = "gy2a9mIJu5QnwyeoQ33n0VUNF39eiwpa"
        query = self.get_argument('hostname')
        api = shodan.Shodan(SHODAN_API_KEY)
        results = api.search(query)
        total = int(results['total'])
        for result in results['matches']: iplist.append({"ip":result['ip_str'],"country":result['location']['country_name']})
        self._data = {"data":iplist,"total":total}

    def GET(self):
        pass
