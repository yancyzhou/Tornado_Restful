# -*- coding:utf-8 -*-
from Handler import BaseHandler
import jwt
import datetime
import hashlib

SECRET = 'my_secret_key'
'''
首页
'''

# 后台系统登录


class AdminLogin(BaseHandler):
    """docstring for Login"""
    # usertype 默认为0 表示普通用户，1表示为管理员用户
    def _set_token(self):
        self.encoded = jwt.encode({
            'user': {'username': self.username, 'userid': 1, 'usertype': 1},
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60)},
            SECRET,
            algorithm='HS256'
        )

    def post(self):
        self.username = self.get_json_argument("username")
        self.passwd = self.get_json_argument('password')

        passwordmd5 = hashlib.md5()
        passwordmd5.update(self.passwd)
        inputpasswrod = passwordmd5.hexdigest()
        # print self.dbs.user.find({'username': self.username})
        passwordmd5.update('root')
        if self.username == 'root' and inputpasswrod == passwordmd5.hexdigest():

            self._set_token()
        response = {'token': self.encoded}
        self.write(response)
