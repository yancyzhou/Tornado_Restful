from app import *

handlers = [
    (r"/reverse/text/(\w+)/width/(\d+)", ReverseHandler),
    (r"/", IndexHandler),
    (r"/parsehtml", ParseHtmls)
]
