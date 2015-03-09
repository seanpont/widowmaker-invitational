#!/usr/bin/env python

import datetime
import json
import webapp2
import logging
from google.appengine.ext import ndb
from lib.router import route, ROUTES
from google.appengine.api import mail
from google.appengine.api import users as google_users


class Config(ndb.Model):
    mail_sender = ndb.StringProperty(required=True)
    invite_code = ndb.StringProperty(default="mhbb")

    @classmethod
    def get(cls):
        return ndb.Key(Config, 'key').get()


class Comment(ndb.Model):
    author = ndb.StringProperty(required=True)
    text = ndb.TextProperty(required=True)
    created_at = ndb.TimeProperty(auto_now_add=True)


class User(ndb.Model):
    # key = email
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=True)

    @classmethod
    def key_for(cls, email):
        return ndb.Key(User, email.lower())

    @classmethod
    def get_by_email(cls, email):
        return cls.key_for(email.lower()).get()

    @classmethod
    @ndb.transactional()
    def create(cls, name, email):
        if not cls.key_for(email).get():
            return User(id=email.lower(), name=name, email=email.lower()).put().get()


def to_dict(model):
    assert isinstance(model, ndb.Model)
    model_dict = model.to_dict()
    model_dict['id'] = model.key.id()
    return model_dict


datetime_handler = lambda obj: obj.strftime("%Y-%m-%d %H:%M:%S") if isinstance(obj, datetime.datetime) else None


class BaseHandler(webapp2.RequestHandler):
    def initialize(self, request, response):
        super(BaseHandler, self).initialize(request, response)

    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render(self, data):
        if not data:
            return
        if isinstance(data, ndb.Model):
            data = to_dict(data)
        elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], ndb.Model):
            data = [to_dict(m) for m in data]
        json_txt = json.dumps(data, default=datetime_handler)
        logging.info(self.request.path + ' response: ' + json_txt)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.write(json_txt)

    def _get(self):
        self.abort(404)

    def _post(self):
        self.abort(404)

    def get(self):
        self.render(self._get())

    def post(self):
        self.render(self._post())

    def params(self, *args):
        """get request parameter(s)"""
        logging.info(self.request.body)
        req = json.loads(self.request.body)
        if len(args) == 1:
            return req.get(args[0])
        return (req.get(arg) for arg in args)


@route('/app/register')
class RegistrationHandler(BaseHandler):
    def post(self):
        config = Config.get()
        if not config:
            self.abort(500, "Site is not properly configured")
        name, email, code = self.params('name', 'email', 'code')
        if not name or not email or not code:
            self.abort(400, "All parameters requrired")
        if code != config.invite_code:
            self.abort(401, "Incorrect invite code")
        email = email.lower()
        user = User.create(name, email)
        if user:
            mail.send_mail(config.mail_sender, email, "Widowmaker Invitational", "You're In!")
        return user


@route('/app/comments')
class CommentsHandler(BaseHandler):
    def _get(self):
        return Comment.query().order(Comment.created_at).fetch()

    def _post(self):
        author, text = self.params('author', 'text')
        if not author or not text:
            self.abort(400, 'author and text required')
        Comment(author=author, text=text).put()


@route('/app/admin')
class ConfigHandler(BaseHandler):
    def _get(self):
        user = google_users.get_current_user()
        if not user:
            login_url = google_users.create_login_url(self.request.url)
            return self.redirect(login_url)
        if not google_users.is_current_user_admin():
            return self.abort(401)

    def _post(self):
        if not google_users.is_current_user_admin():
            self.abort(401)
        config = Config.get() or Config()
        config.mail_sender = self.params('mail_sender')
        config.put()




















app = webapp2.WSGIApplication(ROUTES, debug=True)


