from models import *

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

def get_games_hosted_by(user):
    """ return games which is being hosted by user 
    """
    games = []
    games = GameModel.all()\
                     .filter("created_by =", user)
                     
    if games.count() > 0:
        games = games.order("-modified_time")

    return games

def put_session(user, token, secret):
    session_model = SessionModel(user=user, token=token,
                                 secret=secret)
    session_model.put()
    
    return session_model

