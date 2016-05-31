# -*- coding:utf-8 -*-
import jwt
from Handler import *
from tornado.escape import json_decode, json_encode
secret_key = "my_secret_key"
options = {
    'verify_signature': True,
    'verify_exp': True,
    'verify_nbf': False,
    'verify_iat': True,
    'verify_aud': False
}


def jwtauth(handler_class):
    ''' Handle Tornado JWT Auth '''
    def wrap_execute(handler_execute):
        def require_auth(handler, kwargs):

            auth = handler.request.headers.get('Authorization')
            if auth:
                parts = auth.split()

                if parts[0].lower() != 'bearer':
                    handler._transforms = []
                    handler.writejson(json_decode(str(ApiHTTPError(10405))))
                    handler.finish()
                elif len(parts) == 1:
                    handler._transforms = []
                    handler.writejson(json_decode(str(ApiHTTPError(10405))))
                    handler.finish()
                elif len(parts) > 2:
                    handler._transforms = []
                    handler.writejson(json_decode(str(ApiHTTPError(10405))))
                    handler.finish()

                token = parts[1]
                print token
                try:
                    res = jwt.decode(
                        token,
                        secret_key,
                        options=options
                    )
                    print res
                except Exception, e:
                    handler._transforms = []
                    handler.set_status(200)
                    handler.writejson({'message': e.message, 'code': 10416})
                    handler.finish()
            else:
                handler._transforms = []
                handler.writejson(json_decode(str(ApiHTTPError(10402))))
                handler.finish()

            return True

        def _execute(self, transforms, *args, **kwargs):

            try:
                require_auth(self, kwargs)
            except Exception:
                return False

            return handler_execute(self, transforms, *args, **kwargs)

        return _execute

    handler_class._execute = wrap_execute(handler_class._execute)

    return handler_class
