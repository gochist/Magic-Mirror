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

class TwitSigninHandler(webapp.RequestHandler):
    def get(self):
        # get request token
        twit = OAuthApi()
        req_token = twit.getRequestToken()
        
        # insert request token into DB
        req_token_model = OAuthRequestToken(token=req_token.key, 
                                            secret=req_token.secret)
        req_token_model.put()
        
        logging.info("req_token is made: %s"%req_token)
        
        # redirect user to twitter auth page
        auth_url = twit.getAuthorizationURL(req_token)
        self.redirect(auth_url)
                

class MainHandler(webapp.RequestHandler):
    def get(self):
        write = self.response.out.write
        write("<a href='/oauth/twitter/signin'>sign in with twitter</a>")
        
#        client = OAuthClient('twitter', self)
#        
#        query = QuestionModel.all().order('created_time')
#        template_dict['user'] = client.get_cookie()                
#        template_dict['questions'] = query.fetch(10)
#        
#        if template_dict['user']:
#            try:
#                info = client.get('/account/verify_credentials')
#                info2 = client.get('/statuses/user_timeline')
#                template_dict['profile_image_url'] = info['profile_image_url']
#                import pprint
#                template_dict['info2'] = pprint.pformat(info)
#            except :
#                client.cleanup()
#            
#        
#        twit = OAuthApi()
#        req_token = twit.getRequestToken()
#        
#        req_token_model = OAuthRequestToken(token=req_token.key,
#                                            secret=req_token.secret)
#        req_token_model.put()
#        
#        auth_url = twit.getAuthorizationURL(req_token)
#        self.redirect(auth_url)

class TwitCallbackHandler(webapp.RequestHandler):
    def get(self):
        req_token = None        
        token = self.request.get("oauth_token")
        logging.info("oauth token in callback handler request : %s"%token)
        query = OAuthRequestToken.all().filter('token =', token)
        
        if query.count() > 0:
            req_token = query.fetch(1)[0]            
        else:
            raise Exception
        
        req_token = oauth.OAuthToken(req_token.token, req_token.secret)
        
        twit = OAuthApi(access_token=req_token)
        access_token = twit.getAccessToken()
        
        twit = OAuthApi(access_token=access_token)
        
        user = twit.GetUserInfo()
        self.response.out.write(user.GetName())
#                
#        ret = twit.PostUpdates("test")
#        self.response.out.write(cgi.escape(ret))
       
        
#        template_dict = {}        
#        ret = template.render(os.path.join(config.tpl_path, 'main.html'),
#                              template_dict)
#        self.response.out.write(ret)
            
class QuestionHandler(webapp.RequestHandler):
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
        

class OAuthHandler(webapp.RequestHandler):
    def get(self, service, action=''):
#        if service not in config.OAUTH_APP_SETTINGS:
#            return self.response.out.write("Unknown OAuth Service Provider: %r" 
#                                           % service)
#
#        client = OAuthClient(service, self)
#        if action in client.__public__:
#            self.response.out.write(getattr(client, action)())
#        else:
#            self.response.out.write(client.login())        
        pass
