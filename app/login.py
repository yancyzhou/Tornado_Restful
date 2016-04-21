# -*- coding:utf-8 -*-
import tornado.web
import jwt
import datetime
SECRET = 'my_secret_keys'


class AuthHandler(tornado.web.RequestHandler):

    def prepare(self):
        self.encoded = jwt.encode({
            'user': {'username': 'Vincent', 'userid': 1},
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)},
            SECRET,
            algorithm='HS256'
        )

    def _set_token(self):
        self.encoded = jwt.encode({
            'user': {'username': self.username, 'userid': 1},
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)},
            SECRET,
            algorithm='HS256'
        )

    def get(self):
        response = {'token': self.encoded}
        self.write(response)

    def post(self):
        self.username = self.get_argument('username')
        self.passwd = self.get_argument('passwd')
        self._set_token()
        response = {'token': self.encoded}
        self.write(response)
