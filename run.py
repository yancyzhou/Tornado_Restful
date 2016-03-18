# -*- encoding:utf-8 -*-
import motor
from tornado import httpserver, ioloop, options as Options, web, platform
from config import *
from utils import *
from tornado.options import define, options

define("port", default=Webservers_port, help="run on the given port", type=int)
# from tornado.netutil import Resolver
#
# Resolver.configure('platform.caresresolver.CaresResolver')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = Handlers
        settings = Settings
        client = motor.motor_tornado.MotorClient(DB, Port)
        # client = pymongo.Connection("localhost", 27017)
        self.db = client[Collections]
        web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    Options.parse_command_line()
    http_server = httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()
