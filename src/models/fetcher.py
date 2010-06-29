from models import *
from datetime import datetime
import config

###########################################
# related on game result operation
def get_gamer_list(game_id, option=None, invert=False):
    game = GameModel.get_by_id(game_id)
    maps = OptionUserMapModel.all()\
                             .filter('game =', game)
    
    if option:
        if invert:
            return [map.user for map in maps 
                    if map.option_no != option]
        else:
            return [map.user for map in maps 
                    if map.option_no == option]
    else:
        return [map.user for map in maps]

def get_final_score(user):
    query = ScoreModel.all()\
                      .filter('user =', user)\
                      .order('-created_time')

    if query.count() > 0:
        return query.fetch(1)[0].final_score
    else:
        return 0.0                       

def set_score(user, game_id, score):
    final_score = get_final_score(user)
    game = GameModel.get_by_id(game_id)
    model = ScoreModel(user=user, game=game, score=score,
                       final_score=final_score + score)
    model.put()
    
    return model

def set_game_result(game_id, option):
    game = GameModel.get_by_id(game_id)
    game.result = option
    game.put()
    
    return game


###########################################
# related on user operation
def get_user_by_twitid(twit_id):
    user = None
    query = UserModel.all().filter("twit_id =", twit_id)
    
    if query.count > 0 :
        user = query.fetch(1)[0]
    
    return user

def set_user(twit_id, twit_screen_name, twit_img_url):
    user = get_user_by_twitid(twit_id)
    if user:
        user.twit_id = twit_id
        user.twit_screen_name = twit_screen_name
        user.twit_img_url = twit_img_url
    else:
        user = UserModel(twit_id=twit_id,
                         twit_screen_name=twit_screen_name,
                         twit_img_url=twit_img_url)

    user.put()
    return user
   

###########################################
# related on game list
def get_games_playing_by(user):
    """ return games which is playing by user 
    """
    games = []
    maps = OptionUserMapModel.all()\
                             .filter("user =", user)

    if maps.count() > 0:
        maps = maps.order("-modified_time")
        games = [map.game for map in maps if map.game.result == -1]

    return games

def get_games_near_deadline():
    games = GameModel.all() \
                     .filter('deadline >', datetime.utcnow())
    if games.count() > 0:
        games = games.order('deadline')
         
    return games

def get_games_hosted_by(user):
    """ return games which is being hosted by user 
    """
    games = GameModel.all()\
                     .filter("created_by =", user)
                     
    if games.count() > 0:
        games = games.order("-modified_time")

    return games

def get_games_by_pageview():
    games = GameModel.all().order('-view')
    return games


###########################################
# related on auth
def put_session(user, token, secret):
    session_model = SessionModel(user=user, token=token,
                                 secret=secret)
    session_model.put()
    
    return session_model

def put_req_token(token, secret, return_url):
    req_token_model = OAuthRequestToken(token=token,
                                        secret=secret,
                                        return_url=return_url)
    req_token_model.put()
        
def get_req_token_by_oauth_token(token):
    query = OAuthRequestToken.all()\
                             .filter('token =', token)
    if query.count() > 0:
        return query.fetch(1)[0]
    else:
        return None
    
def delete_req_token_by_model(token):
    db.delete(token)    

def check_session(sid, extend=True):
    session = SessionModel.get(sid)
    if session:
        if datetime.utcnow() - session.modified > config.session_life:
            return None
        elif extend:
            session.put()
        
    return session
              