# -*- coding:utf-8 -*-
import tornado.web
import jwt
from Handler import Handler, ApiHTTPError
import datetime
import hashlib
from tornado import gen
from tornado.escape import json_decode, json_encode

SECRET = 'my_secret_key'

'''
登录成功生成toke
'''


class AuthHandler(Handler):

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
        self.username = self.get_json_argument("username")
        self.passwd = self.get_json_argument('password')

        passwordmd5 = hashlib.md5()
        passwordmd5.update(self.passwd)
        inputpasswrod = passwordmd5.hexdigest()
        print self.dbs.user.find({'username': self.username})
        passwordmd5.update('root')
        if self.username == 'root' and inputpasswrod == passwordmd5.hexdigest():

            self._set_token()
        response = {'token': self.encoded}
        self.write(response)

"""
add new user
"""


class AddUser(Handler):
    """docstring for AddUser"""

    @gen.coroutine
    def post(self):
        self.username = self.get_json_argument('username')
        self.passwd = self.get_json_argument('password')

        result = yield self.dbs.user.find({'username': self.username}).to_list(1)
        if len(result) > 0:
            self.writejson(json_decode(str(ApiHTTPError(20201))))
        else:
            if len(self.passwd) < 6 or len(self.passwd) > 15:
                self.writejson(json_decode(str(ApiHTTPError(20001))))
            else:
                passwordmd5 = hashlib.md5()
                passwordmd5.update(self.passwd)
                inputpasswrod = passwordmd5.hexdigest()
                document = {}
                document['username'] = self.username
                document['password'] = inputpasswrod
                document['is_admin'] = 0
                document['group'] = 0
                result = yield self.dbs.user.insert(document)
                self.writejson({'userid': repr(result)})
