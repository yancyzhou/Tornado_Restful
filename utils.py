from app import *
from Handler import ErrorHandler
Handlers = [
    (r"/reverse/text/(\w+)/width/(\d+)", ReverseHandler),
    (r"/getuserinfo", IndexHandler),
    (r".*", ErrorHandler),
]
