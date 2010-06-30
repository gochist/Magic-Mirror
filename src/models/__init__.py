from google.appengine.ext import db

class UserModel(db.Model):
    twit_id = db.StringProperty(required=True)
    twit_screen_name = db.StringProperty(required=True)
    twit_img_url = db.StringProperty(required=True)
    score = db.IntegerProperty(default=0)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)
    final_score = db.FloatProperty(default=0.0)

class OAuthRequestToken(db.Model):
    token = db.StringProperty()
    secret = db.StringProperty()
    return_url = db.StringProperty(default='/')
    created = db.DateTimeProperty(auto_now_add=True)
    
class SessionModel(db.Model):
    user = db.ReferenceProperty(UserModel, required=True)
    token = db.StringProperty(required=True)
    secret = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

class GameModel(db.Model):
    subject = db.StringProperty(required=True)
    deadline = db.DateTimeProperty(required=True)
    options = db.StringListProperty(required=True)
    created_by = db.ReferenceProperty(UserModel, required=True)    
    created_time = db.DateTimeProperty(auto_now_add=True)
    modified_time = db.DateTimeProperty(auto_now=True)
    view = db.IntegerProperty(default=0)
    result = db.IntegerProperty(default=-1)
    
    def has_result(self):
        return self.result != -1

class ScoreModel(db.Model):
    user = db.ReferenceProperty(UserModel, required=True)
    game = db.ReferenceProperty(GameModel, required=True)
    score = db.FloatProperty(required=True)
    final_score = db.FloatProperty(required=True)
    created_time = db.DateTimeProperty(auto_now_add=True)


class OptionUserMapModel(db.Model):
    user = db.ReferenceProperty(UserModel, required=True)
    game = db.ReferenceProperty(GameModel, required=True)
    option_no = db.IntegerProperty(required=True)
    created_time = db.DateTimeProperty(auto_now_add=True)
    modified_time = db.DateTimeProperty(auto_now=True)

class MessageModel(db.Model):
    user = db.ReferenceProperty(UserModel, required=True)
    game = db.ReferenceProperty(GameModel, required=True)
    text = db.StringProperty(required=True)
    created_time = db.DateTimeProperty(auto_now_add=True)
    
