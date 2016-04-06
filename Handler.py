from tornado.web import RequestHandler, StaticFileHandler
from tornado.web import HTTPError
from Error_config import Errortypes
from tornado.escape import json_decode, json_encode
import os


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

    def writejson(self, obj):
        self.write(obj), 200, {'Content-Type': 'application/json;'}

    def get(self, *args, **kwargs):
        self.writejson(json_decode(str(ApiHTTPError(10405))))

    def post(self, *args, **kwargs):
        self.writejson(json_decode(str(ApiHTTPError(10405))))


class ErrorHandler(Handler):
    def get(self):
        self.writejson(json_decode(str(ApiHTTPError(10404))))

    def post(self):
        self.writejson(json_decode(str(ApiHTTPError(10404))))
