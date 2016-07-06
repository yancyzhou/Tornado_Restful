from app import *
from admin import *
from Handler import NotFound
Handlers = [
    # (r"/reverse/text/(\w+)/width/(\d{1,2})", ReverseHandler),
    (r'/api/auth', AuthHandler),
    (r'/api/adduser', AddUser),
    (r'/api/search', GetUrlAll),
    (r'/api/getrule', GetrRuleAll),
    (r'/api/addrule', AddRule),
    (r'/api/VerificationUrl', VerificationUrl),
    (r".*", NotFound),
]
