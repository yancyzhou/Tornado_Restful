from app import *
from admin import *
from Handler import NotFound
Handlers = [
    # (r"/reverse/text/(\w+)/width/(\d{1,2})", ReverseHandler),
    (r'/api/auth', AuthHandler),
    (r'/api/adduser', AddUser),
    (r'/api/search', GetUrlAll),
    (r'/api/getrule', GetrRuleAll),
    (r'/api/test', test),
    (r'/api/addrule', AddRule),
    (r'/api/delrule', DelRule),
    (r'/api/shodan', getshodan),
    (r'/api/VerificationUrl', VerificationUrl),
    (r'/api/getmonth', getMonth),
    (r'/api/getmonthprovinces', getMonthProvinces),
    (r'/api/getmonthprovincessschool', getMonthProvincesschool),
    (r'/api/getmonthprovincesssale', getMonthProvincessales),
    (r'/api/getday', getday),
    (r'/api/getexamdata', getexamdata),
    (r'/api/getexamdaydata', getexamdaydata),
    (r'/api/getexammonthdata', getexammonthdata),
    (r".*", NotFound),
]
