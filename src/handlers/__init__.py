# -*- coding: utf-8 -*-
import logging
from google.appengine.api.urlfetch_errors import DownloadError
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from models import *
from models import fetcher
import config, os, datetime
from oauthtwitter import OAuthApi
import oauth
import utils
import urllib

class BaseHandler(webapp.RequestHandler):
    # cookie related functions
    def set_cookie(self, key, value, path='/',
                   expires='Fri, 15-Jun-2012 23:59:59 GMT'):
        """Set cookie. """
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
        # set cookie sid
        session = fetcher.put_session(user, token, secret)
        sid = session.key()
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
        session = fetcher.check_session(sid, extend)
        return session
    
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
        
        
    def make_game_list(self, games, n=10):
        ret = ""
        if not games : 
            return ""
        
        for game in games[:n]:
            ret += self.render_module("game_preview.html", game=game)
        
        logging.info(ret)
        
        return ret
        

class TwitSigninHandler(BaseHandler):
    def get(self):
        # check session
        session = self.get_vaild_session(extend=False)
        if session:
            self.delete_session(session)
        
        # get request token
        twit = OAuthApi()
        try:
            req_token = twit.getRequestToken()
        except DownloadError:
            self.redirect("/?msg=error")
            return
        
        # return url control
        return_url = urllib.unquote(self.request.get('return_url'))
        
        # insert request token into DB
        fetcher.put_req_token(req_token.key, req_token.secret, return_url)
        
        # redirect user to twitter auth page
        auth_url = twit.getAuthorizationURL(req_token)
        self.redirect(auth_url)
        
class TwitSignoutHandler(BaseHandler):
    def get(self):
        # check session
        session = self.get_vaild_session(extend=False)
        if session:
            self.delete_session(session)

        # go home
        self.redirect("/")        

class TwitCallbackHandler(BaseHandler):
    def get(self):
        # get req token from DB
        token = self.request.get("oauth_token")
        req_token = fetcher.get_req_token_by_oauth_token(token)
        if not req_token:
            self.redirect('/oauth/twitter/signin')
            return
        
        # model to object
        req_token_obj = oauth.OAuthToken(req_token.token, req_token.secret)
        return_url = req_token.return_url
        
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
        fetcher.delete_req_token_by_model(req_token)
        
        # get user info 
        try:
            twit = OAuthApi(access_token=access_token)
        except DownloadError:
            self.redirect("/?msg=error")
            return
        
        user = twit.GetUserInfo()

        # add user 
        user_model = fetcher.set_user(twit_id=str(user.id),
                                      twit_screen_name=user.screen_name,
                                      twit_img_url=user.profile_image_url)
        
        
        # add session
        self.new_session(user_model, token, secret)        
        
        # redirect to home
        if not return_url:
            return_url = '/' 
        self.redirect(return_url)

class TimelineHandler(BaseHandler):
    def get(self):
        session = self.get_vaild_session()        

        # near deadline
        games = fetcher.get_games_near_deadline()
        near_deadline_list = self.make_game_list(games)
        
        # hot games
        games = fetcher.get_games_by_pageview()
        hot_game_list = self.make_game_list(games)
        
        self.render_page(main_module='public_timeline.html',
                         side_module='introduce.html',
                         session=session,
                         near_deadline=near_deadline_list,
                         hot_games=hot_game_list)        

class GameResultHandler(BaseHandler):    
    def get(self, game_id, option_no):
        """ Set final result of game as input parameter.
        """
        game_id = int(game_id)
        option_no = int(option_no)
        
        session = self.get_vaild_session()
        if not session:
            self.redirect('/%s' % game_id)
            return

        # get all gamers, winners, losers
        winners = fetcher.get_gamer_list(game_id=game_id, option=option_no)
        losers = fetcher.get_gamer_list(game_id=game_id, option=option_no,
                                        invert=True)

        # calc score        
        if winners and losers :
            score = float(len(losers)) / len(winners)
            lost_score = -1.0
        else:
            score = 0.0
            lost_score = 0.0
            
        # set score TODO: make it as a transaction
        for winner in winners:
            fetcher.get_final_score(winner)
            fetcher.set_score(winner, game_id, score)

        for loser in losers:
            fetcher.get_final_score(loser)
            fetcher.set_score(loser, game_id, lost_score)
            
        # set game result
        game = fetcher.set_game_result(game_id, option_no)
        
        self.redirect('/%s' % game_id)
        

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
        
class MsgDeleteHandler(BaseHandler):
    def get(self, msg_key):
        session = self.get_vaild_session()
        message = db.get(msg_key)
        game = message.game
        
        if session.user.key().id() == message.user.key().id():
            message.delete()
        
        self.redirect("/%s" % game.key().id())        

class GameViewHandler(BaseHandler):
    def get(self, game_id):
        game_id = int(game_id)

        session = self.get_vaild_session()
        game = GameModel.get_by_id(game_id)
        # FIXME:
        if not game:
            self.redirect('/')
            return
        
        option_game_map = []
        for i, option in enumerate(game.options):
            gamers = OptionUserMapModel.all()\
                                       .filter('game =', game)\
                                       .filter('option_no =', i)\
                                       .order('modified_time')
            option_game_map.append((option, gamers, i))
            
        query = MessageModel.all()\
                            .filter('game =', game)\
                            .order('-created_time')
                            
        if query.count() > 0 :                                
            messages = query.fetch(100)
        else :
            messages = []
            
        return_url_param = "?" + urllib.urlencode({'return_url': 
                                                   "/%s" % game.key().id()})
        
        
        intime = game.deadline > datetime.datetime.utcnow()
        
        game.view = game.view + 1
        game.put()
        
        scores = ScoreModel.all()\
                          .filter('game =', game)\
                          .order('-score')
                          
        
        self.render_page(main_module='game_view.html',
                         side_module='game_stats.html',
                         session=session,
                         game=game,
                         messages=messages,
                         option_game_map=option_game_map,
                         intime=intime,
                         scores=scores,
                         google_visualization=True,
                         jquery=True,
                         return_url_param=return_url_param,
                         config=config)
    
    def post(self, game_id, mode):
        game_id = int(game_id)
        session = self.get_vaild_session()
        game = GameModel.get_by_id(game_id)
        
        if (not session) or (not game):
            self.redirect('/%d' % game_id)   
            return
        
        if mode == 'msg':
            text = self.request.get('message') \
                               .replace('\r', '') \
                               .replace('\n', '')

            tweet_it = self.request.get('tweet_it')

            message = MessageModel(user=session.user, game=game,
                                   text=text)
            message.put()

            logging.info(tweet_it)
            
            if tweet_it:
                twit = self.get_twitapi(session)
                ret = twit.PostUpdate(message.text)
            
            self.redirect('/%d' % game_id)
            return
        
            
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
        
        if not user_info.utc_offset:
            user_info.utc_offset = 0
        if not user_info.time_zone :
            user_info.time_zone = "GMT" 
        
        utc_offset_hour = user_info.utc_offset / (3600.0)
        tz_str = "%s(UTC%+02.1f)" % (user_info.time_zone, utc_offset_hour) 
        
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
        
        page_dict = {'subject' :self.request.get('subject').strip()}
        page_dict['options'] = [line.strip() for line 
                                             in self.request.get('option')\
                                                            .strip()\
                                                            .splitlines() 
                                             if line]
        # get user information
        twit = self.get_twitapi(session)
        user_info = twit.GetUserInfo()
                
        # validate form
        if not user_info.utc_offset:
            user_info.utc_offset = 0         
        utc_offset = user_info.utc_offset
        due_date = self.request.get('due_date')
        due_time = self.request.get('due_time')
        deadline = due_date + due_time
        page_dict['deadline'] = utils.utc_time(deadline, utc_offset)
        
        # pack data
        
        if not self.validate_form(page_dict):
            self.redirect('/game/new')
            return
        
        
        # insert game into DB
        game = GameModel(subject=page_dict['subject'],
                         options=page_dict['options'],
                         deadline=page_dict['deadline'],
                         created_by=session.user,
                         result= -1)
        game.put()
        
        # implement twit msg
        tweet_it = self.request.get('tweet_it')
        if tweet_it:
            url = config.hosturl + "/" + str(game.key().id())
            msg = game.subject[:135 - len(url)] + " " + url
            twit = self.get_twitapi(session)
            twit.PostUpdate(msg)
            
            logging.info("twit this! " + msg)
            
        # redirect
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

        joined_games = ""
        games = fetcher.get_games_playing_by(session.user)
        joined_games = self.make_game_list(games)           

        # hosted by me
        hosted_games = ""
        games = fetcher.get_games_hosted_by(session.user)
                         
        if games:
            hosted_games = self.make_game_list(games)
        
        scores = ScoreModel.all()\
                           .filter('user =', session.user)\
                           .order('-created_time')
        
        # render page
        self.render_page(main_module='user_home.html',
                         side_module='user_stats.html',
                         session=session,
                         joined_games=joined_games,
                         hosted_games=hosted_games,
                         scores=scores,
                         user=user_info)
        

       

class MainHandler(BaseHandler):
    def get(self):
        session = self.get_vaild_session()
        if session :
            self.redirect('/home')
            return
        
        else :
            self.redirect('/timeline')
            return


       
class TestHandler(BaseHandler):
    def get(self):
        # setting user
        query = UserModel.all().filter('twit_id =', '15640669')
        if query.count() :
            db.delete(query.fetch(1))
            
        user = UserModel(twit_id='15640669', twit_screen_name='gochist',
                         twit_img_url='http://a1.twimg.com/profile_images/64147960/gochist_normal.JPG',
                         score=123)
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

