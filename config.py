# -*- coding:utf-8 -*-
'''
======================
@author Vincent
======================
'''
import os
from app import *

# 起服务的端口
Webservers_port = 8003
# 数据库的地址
DB = 'localhost'
# 数据库的端口
Port = 27017
# mongodb的集合名称Collection
Collections = 'yancy'
Settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    ui_modules={},
    debug=True,
)
