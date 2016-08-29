# -*- encoding:utf-8 -*-
import motor
from tornado import httpserver, ioloop, options as Options, web, platform
from config import *
from utils import *
from tornado.options import define, options
import pymongo
import click
# @click.group(invoke_without_command=True)
@click.command()
@click.option('--port', default=Webservers_port, help='webui port')
def cli(**kwargs):
    define("port", default=kwargs['port'], help="run on the given port", type=int)
    Options.parse_command_line()
    http_server = httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    ioloop.IOLoop.instance().start()

# from tornado.netutil import Resolver
#
# Resolver.configure('platform.caresresolver.CaresResolver')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = Handlers
        settings = Settings
        client = motor.motor_tornado.MotorClient(DB, Port)
        clientpy = pymongo.Connection(DB, Port)
        self.db = client[Collections]
        self.dbpy = clientpy[Collections]
        web.Application.__init__(self, handlers, **settings)

if __name__ == "__main__":
    cli()
