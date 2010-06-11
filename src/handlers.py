# -*- coding: utf-8 -*-
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
#from google.appengine.ext.webapp.util import login_required
from models import *
import config, os, cgi
#from util import twit_login_required
from oauthtwitter import OAuthApi
import oauth

class BaseHandler(webapp.RequestHandler):
    def set_cookie(self, key, value, path='/', expires='Session'):
        add_header = self.response.headers.add_header
        data_dict = {'key' : key,
                     'value': value,
                     'path':path,
                     'expires':expires}
        add_header('Set-Cookie',
                   '%(key)s=%(value)s; path=%(path)s; expires="%(expires)s"' % 
                   data_dict)
    
    def get_cookie(self, key):
        return self.request.cookies.get(key, '')
    
    def expire_cookie(self, key, path='/'):
        self.set_cookie(key, '', path, 'Fri, 31-Dec-1999 23:59:59 GMT')
        

class TwitSigninHandler(BaseHandler):
    def get(self):
        # get request token
        twit = OAuthApi()
        req_token = twit.getRequestToken()
        
        # insert request token into DB
        req_token_model = OAuthRequestToken(token=req_token.key,
                                            secret=req_token.secret)
        req_token_model.put()
        
        logging.info("req_token is made: %s" % req_token)
        
        # redirect user to twitter auth page
        auth_url = twit.getAuthorizationURL(req_token)
        self.redirect(auth_url)
        
class TwitSignoutHandler(BaseHandler):
    def get(self):
        self.expire_cookie("twitter")
        self.redirect("/")        
                



class TwitCallbackHandler(BaseHandler):
    def get(self):
        req_token = None        
        token = self.request.get("oauth_token")
        logging.info("oauth token in callback handler request : %s" % token)
        query = OAuthRequestToken.all().filter('token =', token)
        
        if query.count() > 0:
            req_token = query.fetch(1)[0]            
        else:
            self.response.redirect('/oauth/twitter/signin')
        
        # model to object
        req_token_obj = oauth.OAuthToken(req_token.token, req_token.secret)
        
        # get access token
        twit = OAuthApi(access_token=req_token_obj)
        access_token = twit.getAccessToken()
        
        # get user info 
        twit = OAuthApi(access_token=access_token)
        user = twit.GetUserInfo()
        logging.info(user.id)
        
        # insert session into DB
        session = SessionModel(twit_id=str(user.id), token=access_token.key,
                               secret=access_token.secret)
        session.put()
        
        # set cookie
        self.set_cookie("twitter", user.id)
        self.response.out.write(user.id)

            
class QuestionHandler(BaseHandler):
    def get(self, q_key):
        template_dict = {}
        question = QuestionModel.get(q_key)
        query = OptionModel.all()
        query.filter("question_ref = ", question)
        
        template_dict['options'] = query.fetch(10)
        template_dict['question'] = question
        ret = template.render(os.path.join(config.tpl_path, 'question.html'), template_dict)
        self.response.out.write(ret)
        
        self.request.session


    def post(self):
        question = self.request.get('question')
        options = self.request.get('options')
        twit_it = self.request.get('twit_it')
        try:
            q_model = QuestionModel(text=question)
            q_model.put()
            for option in options.strip().splitlines():
                o_model = OptionModel(question_ref=q_model,
                                      text=option)
                o_model.put()

        except Exception:
            return

#        if twit_it :              
#            client = OAuthClient('twitter', self)
#            client.post(api_method='/statuses/update', status=question)
            
        self.redirect('/')

class MainHandler(BaseHandler):
    def get(self):
        write = self.response.out.write
        twitter_id = self.get_cookie('twitter')
        if not twitter_id :
            write("<a href='/oauth/twitter/signin'>sign in with twitter</a>")
        else :
            query = SessionModel.all().filter('twit_id =', twitter_id)
            if query.count() > 0:
                session = query.fetch(1)[0]
                
                token = oauth.OAuthToken(session.token, session.secret)
                twit = OAuthApi(access_token=token)
                user = twit.GetUserInfo()
                write("hello, %s. " % user.screen_name)
                
            
            write("<a href='/oauth/twitter/signout'>sign out</a>")
