# -*- coding:utf-8 -*-
import tornado.web
import jwt
import datetime
import hashlib
from Handler import Handler, ApiHTTPError
from tornado import gen
from tornado.escape import json_decode, json_encode

SECRET = 'my_secret_key'

'''
登录成功生成toke
'''


class AuthHandler(Handler):

    # def prepare(self):
    #     # print self.get_json_argument('username')
    #     passwordmd5 = hashlib.md5()
    #     passwordmd5.update(self.get_json_argument('password'))
    #     inputpasswrod = passwordmd5.hexdigest()
    #     self.encoded = jwt.encode({
    #         'user': {'username': self.get_json_argument('username'), 'userid': 1},
    #         'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)},
    #         SECRET,
    #         algorithm='HS256'
    #     )

    def _set_token(self):
        self.encodeds = jwt.encode({
            'user': {'username': self.username, 'userid': self.id},
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)},
            SECRET,
            algorithm='HS256')

    @gen.coroutine
    def post(self):
        self.username = self.get_json_argument("username")
        self.passwd = self.get_json_argument('password')

        passwordmd5 = hashlib.md5()
        passwordmd5.update(self.passwd)
        inputpasswrod = passwordmd5.hexdigest()
        userdata = yield self.dbs.user.find({'username': self.username}).to_list(1)
        self.id = str(userdata[0]['_id'])
        if self.username == 'admin' and inputpasswrod == userdata[0]['password']:

            self._set_token()
            response = {'token': self.encodeds}
        else:

            response = json_decode(str(ApiHTTPError(20002)))
        self.writejson(response)

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
