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
from tornado import gen
from urllib import unquote
from Handler import Handler
from bs4 import BeautifulSoup
from auth import jwtauth


@jwtauth
class ReverseHandler(tornado.web.RequestHandler):
    def head(self, frob, frob_id):
        # frob = retrieve_from_db(frob_id)
        print int(frob_id)
        if int(frob_id) > 20:
            self.set_status(200)
        else:
            self.set_status(2001)

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error." % status_code)

    def get(self, input, ints):

        temp = {"data": input[::-1]}

        self.write(temp)


class BookModule(tornado.web.UIModule):
    def render(self, book):
        return self.render_string(
            "modules/book.html",
            book=book,
        )

    def css_files(self):
        return "/static/css/recommended.css"

    def javascript_files(self):
        return "/static/js/recommended.js"


@jwtauth
class StartSpider(Handler):
    """开始抓取数据接口"""

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        fid = self.get_argument('fid')
        if type(fid) is int:
            fid = str(fid)
        elif type(fid) is str:
            fid = fid
        page = str(self.get_argument('page', 1))
        callback = self.get_argument('callback', None)
        client = tornado.httpclient.AsyncHTTPClient()
        url = 'http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_WEIBO&page=%s&count=200' % (fid, page)
        response = yield tornado.gen.Task(client.fetch, url)
        result = json.loads(response.body)
        if callback:
            responses = yield tornado.gen.Task(client.fetch, callback)
            self.writejson(json.loads(responses.body))
        else:
            self.writejson(result)


@jwtauth
class LongText(Handler):
    """Get Long Text"""

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        uid = self.get_argument('uid')
        if type(uid) is int:
            uid = str(uid)
        elif type(uid) is str:
            uid = uid
        bid = self.get_argument('bid')
        try:
            client = tornado.httpclient.AsyncHTTPClient()
            url = 'http://m.weibo.cn/%s/%s' % (uid, bid)
            response = yield tornado.gen.Task(client.fetch, url)
            html = BeautifulSoup(response.body, "lxml")
            text = html.find('div', class_='weibo-text')
            if text is not None:
                strtext = map(lambda x: str(x.encode('utf-8')), text.contents)
                longtext = ''.join(strtext)
                data = {'data': longtext, 'code': '000'}
            else:
                data = {'data': '', 'code': '2'}
            self.writejson(data)
        except:
            self.writejson({'data': 'system error', 'code': '1'})


@jwtauth
class IndexHandler(Handler):

    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):
        query = self.get_argument('username')
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, "http://m.weibo.cn/n/" + query)
        result = response.headers['set-cookie'].split(';')
        try:
            cookies = ''
            params = {}
            for item in result:
                if 'M_WEIBOCN_PARAMS' in item:
                    cookies = item.split('=')[1]
            for item in unquote(cookies).split('&'):
                temp = item.split('=')
                params[temp[0]] = temp[1]
            fid = params['fid']
            client = tornado.httpclient.AsyncHTTPClient()
            url = 'http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_WEIBO' % fid
            inforesponse = yield tornado.gen.Task(client.fetch, url)
            # print inforesponse.body
            userinfo = json.loads(inforesponse.body)['cards'][0]['card_group'][0]['mblog']['user']
            self.writejson({'data': userinfo, 'fid': fid, 'code': '000'})
        except IndexError, e:
            self.writejson({'data': result, 'code': '1'})


@jwtauth
class Testdata(Handler):
    @gen.coroutine
    def get(self):

        # cons = self.get_argument('db')
        my_dict = {i: i * i for i in xrange(100)}
        # my_set = {i * 15 for i in xrange(100)}
        import ast
        expr = "[1, 2, 3]"
        my_list = ast.literal_eval(expr)
        print my_list
        iterable = ['ahskjahd', 12, 23, 11, 'aaaa']
        # mongodb 模糊查询
        n = self.dbs.resultcollection.find({'project': 'douban'}).limit(20000)
        for item in (yield n.to_list(20000)):
            res.append(item['url'])
        for i, item in enumerate(iterable, 1):
            print i, item
        self.writejson({'data': my_dict})


@jwtauth
class Testdata7netcc(Handler):
    """获取训练样本数据"""
    # def __init__(self, arg):
    #     super(Testdata7netcc, self).__init__()
    #     self.arg = arg
    @tornado.web.asynchronous
    @gen.coroutine
    def get(self):

        client = tornado.httpclient.AsyncHTTPClient()
        code_url = 'http://10.161.165.239:7011/imgsvr/ru'
        code_result = yield tornado.gen.Task(client.fetch, code_url)
        code_result_json = json.loads(code_result.body)
        if code_result_json['status'] == 200:
            schoool_code_list = code_result_json['data']
        schoool_code_list_small = random.sample(schoool_code_list, 200)
        # res = [x['Code'] for x in schoool_code_list_small]
        res = map(lambda x: "http://10.161.165.239:7011/imgsvr/exam?ru="+x['Code'], schoool_code_list_small)
        result = []
        for item in res:
            school_result = yield tornado.gen.Task(client.fetch, item)
            temp_result = json.loads(school_result.body)
            if temp_result['data'] and temp_result['status'] == 200:
                result.append(temp_result)
        self.writejson({'data': result})
