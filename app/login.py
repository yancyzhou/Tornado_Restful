# -*- coding:utf-8 -*-
import tornado.web
import jwt
import datetime
SECRET = 'my_secret_key'


class AuthHandler(tornado.web.RequestHandler):

    def prepare(self):
        self.encoded = jwt.encode({
            'some': 'payload',
            'a': {2: True},
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)},
            SECRET,
            algorithm='HS256'
        )

    def get(self):
        response = {'token': self.encoded}
        self.write(response)

    def post(self):
        response = {'token': self.encoded}
        self.write(response)
