# -*- coding: utf-8 -*-
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
#from google.appengine.ext.webapp.util import login_required
from models import *
import config, os, time
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

    def delete_session(self, session):
        """Delete session from database. And expire cookie.

        Returns:
          Session id will be returned.
        """
        sid = session.key()
        db.delete(session)
        self.expire_cookie("sid")
        
        # log info
        logging.info("session is deleted. SID: %s" % sid)
        return sid
    
    def new_session(self, twit_id, token, secret):
        """Insert new session into database. And set cookie  
                
        Args:
          twit_id : twitter id (should be string)
          token : access token key
          secret : access secret key
        """
        session_model = SessionModel(twit_id=twit_id, token=token,
                                     secret=secret)
        session_model.put()
        
        # set cookie sid
        sid = session_model.key()
        self.set_cookie("sid", sid)
        
        # log info
        logging.info("new session is created. SID: %s" % sid)
        
    
    def get_vaild_session(self, extend=True):
        """Check if the session is vaild
        
        Args:
          extend : after checking, extend session period.
          
        Returns:
          if the session is vaild, session model will be returned. 
          Otherwise, None will be returned.
        """
        sid = self.get_cookie("sid")
        if sid:            
            query = SessionModel.all()\
                                .filter("key =", sid)
#                                .filter("modified >",
#                                        time.time() - config.session_life)         
            if query.count() > 0:
                session = query.fetch(1)[0]
                if extend:
                    session.put() 
                logging.info("session is valid. SID:%s"%session.key()) 
                return session

        return None
    
    def get_twitapi(self, session=None):
        if session:
            token = oauth.OAuthToken(session.token, session.secret)
            twit = OAuthApi(access_token=token)
            return twit
        else :
            return OAuthApi()
        

class TwitSigninHandler(BaseHandler):
    def get(self):
        session = self.get_vaild_session(extend=False)
        if session:
            self.delete_session(session)
            logging.info("Session already exists. " + 
                         "Old session will be deleted and " + 
                         "new one will be genereated")
        
        # get request token
        twit = OAuthApi()
        req_token = twit.getRequestToken()
        
        # insert request token into DB
        req_token_model = OAuthRequestToken(token=req_token.key,
                                            secret=req_token.secret)
        req_token_model.put()
        
        
        # redirect user to twitter auth page
        auth_url = twit.getAuthorizationURL(req_token)
        self.redirect(auth_url)
        
        logging.info("sign in started.")
        
class TwitSignoutHandler(BaseHandler):
    def get(self):
        session = self.get_vaild_session(extend=False)
        if session:
            self.delete_session(session)
        else :
            logging.info("TwitSignoutHandler attempted " + 
                         "to sign out without vaild session")
            
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

        # insert session into DB
        self.new_session(str(user.id), access_token.key, access_token.secret)        
        self.response.out.write(user.id)
        
        # delete OAuthToken
        db.delete(req_token)

            
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
        session = self.get_vaild_session()
        if session :
            twit = self.get_twitapi(session)
            user = twit.GetUserInfo()
            write("hello, %s. " % user.screen_name)
            write("<a href='/oauth/twitter/signout'>sign out</a>")

        else :
            write("<a href='/oauth/twitter/signin'>sign in with twitter</a>")
