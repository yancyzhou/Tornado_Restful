# -*- coding:utf-8 -*-
'''
======================
@author Vincent
======================
'''
import tornado.web
import tornado.httpclient
import urllib2
import re
import textwrap
import json
from tornado import gen
from urllib import unquote
from Handler import Handler
from bs4 import BeautifulSoup

# class ReverseHandler(tornado.web.RequestHandler):
#     def head(self, frob, frob_id):
#         # frob = retrieve_from_db(frob_id)
#         print int(frob_id)
#         if int(frob_id) > 20:
#             self.set_status(200)
#         else:
#             self.set_status(2001)
#
#     def write_error(self, status_code, **kwargs):
#         self.write("Gosh darnit, user! You caused a %d error." % status_code)
#
#     def get(self, input, ints):
#
#         temp = {"data": input[::-1]}
#
#         self.write(temp)
#
#
# class BookModule(tornado.web.UIModule):
#     def render(self, book):
#         return self.render_string(
#             "modules/book.html",
#             book=book,
#         )
#
#     def css_files(self):
#         return "/static/css/recommended.css"
#
#     def javascript_files(self):
#         return "/static/js/recommended.js"


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


class doubanurl(Handler):
    @gen.coroutine
    def get(self):
        # cons = self.get_argument('db')
        res = []
        # mongodb 模糊查询
        n = self.dbs.resultcollection.find({'project': 'douban'}).limit(20000)
        for item in (yield n.to_list(20000)):

            res.append(item['url'])
        self.writejson({'data': res})
