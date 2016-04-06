import tornado.web
import tornado.httpserver
import auth
import tornado.ioloop
import tornado.options
from datetime import datetime
from Handler import Handler


class FeedHandler(tornado.web.RequestHandler, auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self):
        accessToken = self.get_secure_cookie('access_token')
        if not accessToken:
            print accessToken
            self.redirect('/auth/login')
            return

        self.facebook_request(
            "/me/feed",
            access_token=accessToken,
            callback=self.async_callback(self._on_facebook_user_feed))

    def _on_facebook_user_feed(self, response):
        name = self.get_secure_cookie('user_name')
        self.render('home.html', feed=response['data'] if response else [], name=name)

    @tornado.web.asynchronous
    def post(self):
        accessToken = self.get_secure_cookie('access_token')
        if not accessToken:
            self.redirect('/auth/login')

        userInput = self.get_argument('message')

        self.facebook_request(
            "/me/feed",
            post_args={'message': userInput},
            access_token=accessToken,
            callback=self.async_callback(self._on_facebook_post_status))

    def _on_facebook_post_status(self, response):
        self.redirect('/')


class LoginHandler(tornado.web.RequestHandler, auth.FacebookGraphMixin):
    @tornado.web.asynchronous
    def get(self):
        userID = self.get_secure_cookie('user_id')

        if self.get_argument('code', None):
            print self.get_argument('code', None)
            self.get_authenticated_user(
                redirect_uri='http://localhost:8003/auth/login',
                client_id=self.settings['facebook_api_key'],
                client_secret=self.settings['facebook_secret'],
                code=self.get_argument('code'),
                callback=self.async_callback(self._on_facebook_login))
            return
        elif self.get_secure_cookie('access_token'):
            self.redirect('/')
            return

        self.authorize_redirect(
            redirect_uri='http://localhost:8003/auth/login',
            client_id=self.settings['facebook_api_key'],
            extra_params={'scope': 'read_stream,publish_stream'}
        )

    def _on_facebook_login(self, user):
        if not user:
            self.clear_all_cookies()
            raise tornado.web.HTTPError(500, 'Facebook authentication failed')

        self.set_secure_cookie('user_id', str(user['id']))
        self.set_secure_cookie('user_name', str(user['name']))
        self.set_secure_cookie('access_token', str(user['access_token']))
        self.redirect('/')


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_all_cookies()
        self.render('logout.html')


class authlog(Handler):
    def get(self):
        self.writejson({'data': 'this code page'})


class FeedListItem(tornado.web.UIModule):
    def render(self, statusItem):
        dateFormatter = lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S+0000').strftime('%c')
        return self.render_string('entry.html', item=statusItem, format=dateFormatter)
