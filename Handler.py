from tornado.web import RequestHandler, StaticFileHandler
from tornado.web import HTTPError
from Error_config import Errortypes, Valid_Ip
from tornado.escape import json_decode, json_encode, to_unicode
import os
from tornado import gen


def VerifyIP(handler_class):
    def wrap_execute(handler_execute):
        def Is_Valid_Ip(handler, kwargs):
            if kwargs:
                if handler.request.remote_ip in kwargs:
                    pass
                else:
                    handler._transforms = []
                    handler.set_status(200)
                    handler.writejson(json_decode(str(ApiHTTPError(10402))))
                    handler.finish()
            else:
                if handler.request.remote_ip in Valid_Ip:
                    pass
                else:
                    handler._transforms = []
                    handler.set_status(200)
                    handler.writejson(json_decode(str(ApiHTTPError(10402))))
                    handler.finish()
            return True

        def _execute(self, transforms, *args, **kwargs):

            try:
                Is_Valid_Ip(self, kwargs)
            except Exception:
                return False

            return handler_execute(self, transforms, *args, **kwargs)

        return _execute

    handler_class._execute = wrap_execute(handler_class._execute)

    return handler_class


class ApiHTTPError(Exception):
    """An exception that will turn into an HTTP error response.

    Raising an `HTTPError` is a convenient alternative to calling
    `RequestHandler.send_error` since it automatically ends the
    current function.

    To customize the response sent with an `HTTPError`, override
    `RequestHandler.write_error`.

    :arg int status_code: HTTP status code.  Must be listed in
        `httplib.responses <http.client.responses>` unless the ``reason``
        keyword argument is given.
    :arg string log_message: Message to be written to the log for this error
        (will not be shown to the user unless the `Application` is in debug
        mode).  May contain ``%s``-style placeholders, which will be filled
        in with remaining positional parameters.
    :arg string reason: Keyword-only argument.  The HTTP "reason" phrase
        to pass in the status line along with ``status_code``.  Normally
        determined automatically from ``status_code``, but can be used
        to use a non-standard numeric code.
    """
    def __init__(self, status_code, log_message=None, *args, **kwargs):
        self.status_code = status_code
        self.log_message = log_message
        self.args = args
        self.reason = kwargs.get('reason', None)
        if log_message and not args:
            self.log_message = log_message.replace('%', '%%')

    def __str__(self):
        result = json_encode({'code': self.status_code, 'message': Errortypes[self.status_code]})
        return result


class Handler(RequestHandler):
    @property
    def dbs(self):
        return self.application.db

    @property
    def dbspy(self):
        return self.application.dbpy

    @gen.coroutine
    def writejson(self, obj):
        self.write(obj), 200, {'Content-Type': 'application/json;'}
        self.finish()

    def get_json_arguments(self, args, **kwargs):
        result = json_decode(self.request.body)
        for item in args:
            if item in kwargs:
                result[item] = self.get_json_argument(item, kwargs[item])
            else:
                result[item] = self.get_json_argument(item)
            result[item] = self.get_json_argument(item, default)
        return result

    def get(self, *args, **kwargs):
        self.writejson(json_decode(str(ApiHTTPError(10405))))

    def post(self, *args, **kwargs):
        self.writejson(json_decode(str(ApiHTTPError(10405))))

    '''
    Get the json data format
    '''
    def get_json_argument(self, name, default=None):
        args = json_decode(self.request.body)
        name = to_unicode(name)
        if name in args:
            return args[name]
        elif default is not None:
            return default
        else:
            msg = "Missing argument '%s'" % name
            result = json_decode(str(ApiHTTPError(10410)))
            result['message'] = msg
            self.writejson(result)


class NotFound(Handler):
    def get(self):
        self.writejson(json_decode(str(ApiHTTPError(10404))))

    def post(self):
        self.writejson(json_decode(str(ApiHTTPError(10404))))
