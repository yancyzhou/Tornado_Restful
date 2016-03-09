# -*- coding:utf-8 -*-
'''
======================
@author Vincent
======================
'''
import os
from app import *

# 起服务的端口
Webservers_port = 8000
# 数据库的地址
DB = 'localhost'
# 数据库的端口
Port = 27017
# mongodb的集合名称Collection
Collections = 'tender_spider'
Handlers = [
    (r"/reverse/text/(\w+)/width/(\d+)", ReverseHandler),
    (r"/", IndexHandler),
    (r"/parsehtml", ParseHtmls)
]
Settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    ui_modules={"Book": BookModule},
    debug=True,
)
