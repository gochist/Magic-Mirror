# -*- coding: utf-8 -*-
import logging
from google.appengine.api.urlfetch_errors import DownloadError
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from models import *
import config, os, datetime
from oauthtwitter import OAuthApi
import oauth
import utils


class BaseHandler(webapp.RequestHandler):
    # cookie related functions
    def set_cookie(self, key, value, path='/',
                   expires='Fri, 15-Jun-2012 23:59:59 GMT'):
        """Set cookie. 
        
        Args: 
          key:  
          value: 
          path: 
          expires:
        
        Returns:
          None
        """
        add_header = self.response.headers.add_header
        data_dict = {'key': key,
                     'value': value,
                     'path': path,
                     'expires': expires}
        add_header('Set-Cookie',
                   '%(key)s=%(value)s; path=%(path)s; expires="%(expires)s"' % 
                   data_dict)
    
    def get_cookie(self, key):
        return self.request.cookies.get(key, '')
    
    def expire_cookie(self, key, path='/'):
        self.set_cookie(key, '', path, 'Fri, 31-Dec-1999 23:59:59 GMT')

    # session related functions
    def delete_session(self, session):
        """Delete session from database. And expire cookie.

        Returns:
          Session id will be returned.
        """
        sid = session.key()
        db.delete(session)
        self.expire_cookie("sid")

        return sid
    
    def new_session(self, user, token, secret):
        """Insert new session into database. And set cookie  
                
        Args:
          user : instance of UserModel
          token : access token key
          secret : access secret key
        """
        session_model = SessionModel(user=user, token=token,
                                     secret=secret)
        session_model.put()
        
        # set cookie sid
        sid = session_model.key()
        self.set_cookie("sid", sid)
    
    def get_vaild_session(self, extend=True):
        """Check if the session is vaild
        
        Args:
          extend: after checking, extend session period. (not implemented yet)
          
        Returns:
          if the session is vaild, session model will be returned. 
          Otherwise, None will be returned.
        """
        sid = self.get_cookie("sid")
        if sid:            
            session = SessionModel.get(sid)      
            if session:
                # TODO: implement session timeout
#                if session.modified.time() + config.session_life < time.time() :
#                    return None       
                if extend:
                    session.put() 
                return session
        return None
    
    def get_twitapi(self, session=None):
        if session:
            token = oauth.OAuthToken(session.token, session.secret)
            twit = OAuthApi(access_token=token)
            return twit
        else :
            return OAuthApi()
        
    def render_module(self, module, **mod_dict):
        module_path = os.path.join(config.tpl_path, 'module', module)
        return template.render(module_path, mod_dict)
    
    def render_page(self, main_module, side_module, **page_dict):
        main_path = os.path.join(config.tpl_path, 'main', main_module)
        side_path = os.path.join(config.tpl_path, 'side', side_module)
        page_path = os.path.join(config.tpl_path, 'page.html')
        
        page_dict['main_layout'] = template.render(main_path, page_dict)
        page_dict['side_layout'] = template.render(side_path, page_dict)
        
        ret = template.render(page_path, page_dict)
        self.response.out.write(ret)
        

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
        try:
            req_token = twit.getRequestToken()
        except DownloadError:
            self.redirect("/?msg=error")
            return
        
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
            self.redirect('/oauth/twitter/signin')
            return
        
        # model to object
        req_token_obj = oauth.OAuthToken(req_token.token, req_token.secret)
        
        # get access token
        twit = OAuthApi(access_token=req_token_obj)
        try:
            access_token = twit.getAccessToken()
        except DownloadError:
            self.redirect("/?msg=error")
            return
            
        token = access_token.key
        secret = access_token.secret
        # delete OAuthToken
        db.delete(req_token)
        
        # get user info 
        try:
            twit = OAuthApi(access_token=access_token)
        except DownloadError:
            self.redirect("/?msg=error")
            return
        
        user = twit.GetUserInfo()

        # add user 
        user_model = utils.User()
        # FIXME: user info
        if not user.time_zone:
            user.time_zone = "GMT"
        if not user.utc_offset:
            user.utc_offset = 0
             
        logging.info("%s %s"%(user.time_zone, user.utc_offset))
        user_model.set(twit_id=str(user.id),
                       twit_screen_name=user.screen_name,
                       twit_img_url=user.profile_image_url,
                       time_zone=user.time_zone,
                       utc_offset=user.utc_offset)
        
        # add session
        self.new_session(user_model.model, token, secret)        
        
        # redirect to home
        self.redirect('/home')

class TimelineHandler(BaseHandler):
    def get(self):
        session = self.get_vaild_session()        
        games = GameModel.all() \
                         .filter("deadline >", datetime.datetime.now()) \
                         .order("-deadline") \
                         .fetch(10)

        game_list = ""
        for game in games:
            game_list += self.render_module("game_preview.html",
                                            game=game)
                                           
        self.render_page(main_module='public_timeline.html',
                         side_module='introduce.html',
                         session=session,
                         game_preview=game_list)        

class GameJoinHandler(BaseHandler):
    def get(self, game_id, option_no):
        game_id = int(game_id)
        option_no = int(option_no)
                
        session = self.get_vaild_session()
        if not session:
            self.redirect('/%s' % game_id)
            return
        
        game = GameModel.get_by_id(game_id)
        
        query = OptionUserMapModel.all().filter('game = ', game)\
                                        .filter('user = ', session.user)
        if query.count() > 0 :
            option_map = query.fetch(1)[0]
            option_map.option_no = option_no
            option_map.put()
        else : 
            option_map = OptionUserMapModel(user=session.user,
                                            game=game,
                                            option_no=option_no)
            option_map.put()
        
        self.redirect('/%s' % game_id)

class GameViewHandler(BaseHandler):
    def get(self, game_id):
        session = self.get_vaild_session()
        
        game = GameModel.get_by_id(int(game_id))
        # FIXME:
        if not game:
            raise Exception
        
        option_game_map = []
        for i, option in enumerate(game.options):
            gamers = OptionUserMapModel.all()\
                                       .filter('game =', game)\
                                       .filter('option_no =', i)\
                                       .fetch(100)
            option_game_map.append((option, gamers))
            
        
        
        self.render_page(main_module='game_view.html',
                         side_module='game_stats.html',
                         session=session,
                         game=game,
                         option_game_map=option_game_map)

class GameHandler(BaseHandler):
    def validate_form(self, form):
        # TODO: implement this
        return True
    
    def get(self, mode):
        session = self.get_vaild_session()
        if not session:
            self.redirect('/')
            return
            
        # get user information
        twit = self.get_twitapi(session)
        user_info = twit.GetUserInfo()
        
        utc_offset_hour = session.user.utc_offset / (3600.0)
        tz_str = "%s(UTC%+02.1f)" % (session.user.time_zone, utc_offset_hour) 
        
        # render page
        self.render_page(main_module='game_form.html',
                         side_module='post_guide.html',
                         user=user_info,
                         session=session,
                         jquery=True,
                         timezone=tz_str)

    def post(self):
        session = self.get_vaild_session()
        if not session:
            self.redirect('/')
            return
        
        page_dict = {'subject' :self.request.get('subject').strip(),
                     'options' : self.request.get('option',
                                                  allow_multiple=True)}

        # validate form        
        utc_offset = session.user.utc_offset
        due_date = self.request.get('due_date')
        due_time = self.request.get('due_time')
        deadline = due_date + due_time
        page_dict['deadline'] = utils.utc_time(deadline, utc_offset)
        
        # pack data
        
        if not self.validate_form(page_dict):
            self.redirect('/game/new')
            return
        
        # TODO: implement twit msg
        # insert game into DB
        game = GameModel(subject=page_dict['subject'],
                         options=page_dict['options'],
                         deadline=page_dict['deadline'],
                         created_by=session.user)
        game.put()
        self.redirect("/%s" % game.key().id())
        
        
class HomeHandler(BaseHandler):
    def get(self):
        session = self.get_vaild_session()
        if not session:
            self.redirect('/')
            return
        
        # get user information
        twit = self.get_twitapi(session)
        try:
            user_info = twit.GetUserInfo()
        except DownloadError:
            self.redirect("/?msg=error")
            return
           
        
        # render page
        self.render_page(main_module='user_home.html',
                         side_module='user_stats.html',
                         session=session,
                         user=user_info)
       

class MainHandler(BaseHandler):
    def get(self):
        session = self.get_vaild_session()
        if session :
            self.redirect('/home')
            return
        
        games = GameModel.all().order("-deadline").fetch(10)
        game_list = ""
        for game in games:
            game_list += self.render_module("game_preview.html",
                                            game=game)
        
        # render page
        self.render_page(main_module='public_timeline.html',
                         side_module='introduce.html',
                         session=session,
                         game_preview=game_list)
       
class TestHandler(BaseHandler):
    def get(self):
        # setting user
        query = UserModel.all().filter('twit_id =', '15640669')
        if query.count() :
            db.delete(query.fetch(1))
            
        user = UserModel(twit_id='15640669', twit_screen_name='gochist',
                         twit_img_url='http://a1.twimg.com/profile_images/64147960/gochist_normal.JPG',
                         time_zone='Seoul',
                         utc_offset=32400, score=123)
        user.put()

        # setting session                
        session = SessionModel(secret="Uw9Lfo6iansEYfeZ0OfcrlqNxpFExHHOGIDUidUgg",
                               token="15640669-cusYBmGikvntMdQmwk56et6mAj2X09af0az7D0SY",
                               user=user)
        session.put()
        
        self.set_cookie("sid", session.key())
        
        # 
        db.delete(GameModel.all().fetch(100))
        
        self.redirect('/')

