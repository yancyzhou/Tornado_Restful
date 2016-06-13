from app import *
from admin import *
from Handler import ErrorHandler
Handlers = [
    # (r"/reverse/text/(\w+)/width/(\d{1,2})", ReverseHandler),
    (r"/weiboapi/getuserinfo", IndexHandler),
    (r'/api/auth', AuthHandler),
    (r'/api/adduser', AddUser),
    (r'/api/getdata', Testdata),
    (r'/api/getywphoto', yuwen7netcc),
    (r'/api/getpapersimage', GetPapersImage),
    # (r'/doubanurl', doubanurl),
    (r'/getkeywords', GetKeywords),
    (r'/weiboapi/startspider', StartSpider),
    (r'/weiboapi/getlongtext', LongText),
    (r".*", ErrorHandler),
]
