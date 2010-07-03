from models import *
from datetime import datetime
import config

###########################################
# related on game result operation
def get_gamer_list(game_id, option=None, invert=False):
    game = GameModel.get_by_id(game_id)
    maps = OptionUserMapModel.all()\
                             .filter('game =', game)
    
    if option != None:
        if invert:
            return [map.user for map in maps 
                    if map.option_no != option]
        else:
            return [map.user for map in maps 
                    if map.option_no == option]
    else:
        return [map.user for map in maps]

def set_score(user, game_id, score):
    final_score = user.final_score
    game = GameModel.get_by_id(game_id)
    model = ScoreModel(user=user, game=game, score=score,
                       final_score=final_score + score)
    model.put()
    
    user.final_score = model.final_score
    user.put()
    
    return model

def set_game_result(game_id, option):
    game = GameModel.get_by_id(game_id)
    game.result = option
    game.put()
    
    return game

def get_score_history(user):
    scores = ScoreModel.all()\
                       .filter('user =', user)\
                       .order('created_time')
    return scores          

###########################################
# related on user operation

def get_user_order_rank():
    return UserModel.all().order('-final_score')

def get_user_by(key, value):
    user = None
    
    try:
        query = UserModel.all().filter("%s =" % key, value)
        user = query.fetch(1)[0]
    except Exception:
        pass
    
    return user

def get_user_by_twitid(twit_id):
    return get_user_by("twit_id", twit_id)

def get_user_by_twit_screen_name(twit_screen_name):
    return get_user_by("twit_screen_name", 
                       twit_screen_name)

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
def get_games_played_by(user):
    """ return games which is playing by user 
    """
    games = []
    maps = OptionUserMapModel.all()\
                             .filter("user =", user)

    if maps.count() > 0:
        maps = maps.order("-modified_time")
        games = [map.game for map in maps if map.game.result != -1]

    return games

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
                     .filter("created_by =", user)\
                     .filter("deadline >", datetime.utcnow())\
                     .filter("result =", -1)
                     
    if games.count() > 0:
        games = games.order("-deadline")

    return games

def get_games_pending_by(user):
    """ return games which is being hosted by user 
    """
    games = GameModel.all()\
                     .filter("created_by =", user)\
                     .filter("deadline <", datetime.utcnow())\
                     .filter("result =", -1)
                     
    if games.count() > 0:
        games = games.order("-deadline")

    return games

def get_games_by_pageview():
    games = GameModel.all().order('-view')
    return games


def delete_game(game_id):
    game = GameModel.get_by_id(game_id)
    for m in MessageModel.all().filter('game =',game):
        m.delete()
    for m in OptionUserMapModel.all().filter('game =',game):
        m.delete()
    for m in ScoreModel.all().filter('game =',game):
        m.delete()
    game.delete()    



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
    try:
        session = SessionModel.get(sid)
    except Exception:
        session = None
        
    if session:
        if extend:
            session.put()
#        if datetime.utcnow() - session.modified > config.session_life:
#            return None
        
    return session
