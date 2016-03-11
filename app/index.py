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


class StartSpider(Handler):
    """开始抓取数据接口"""
    def __init__(self, uid, callback=None):
        super(StartSpider, self).__init__()
        self.uid = uid

    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        url = 'http://m.weibo.cn/page/json?containerid=%s_-_WEIBO_SECOND_PROFILE_WEIBO' % self.uid
        response = yield tornado.gen.Task(client.fetch, url)


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
            self.writejson({'data': userinfo})
        except IndexError, e:
            self.writejson({'data': result})
