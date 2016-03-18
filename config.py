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
Collections = 'tender_spider'
Settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    ui_modules={"Book": BookModule, 'FeedListItem': FeedListItem},
    debug=True,
    facebook_api_key='2040 ... 8759',
    facebook_secret='eae0 ... 2f08',
    cookie_secret='NTliOTY5NzJkYTVlMTU0OTAwMTdlNjgzMTA5M2U3OGQ5NDIxZmU3Mg=='
)
