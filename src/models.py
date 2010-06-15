from google.appengine.ext import db

class UserModel(db.Model):
    twit_id = db.StringProperty(required=True)
    twit_screen_name = db.StringProperty(required=True)
    twit_img_url = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

class OAuthRequestToken(db.Model):
    token = db.StringProperty()
    secret = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    
class SessionModel(db.Model):
    user = db.ReferenceProperty(UserModel, required=True)
    token = db.StringProperty(required=True)
    secret = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

class QuestionModel(db.Model):
    text = db.StringProperty(required=True)
    created_by = db.ReferenceProperty(UserModel)    
    created_time = db.DateTimeProperty(auto_now_add=True)
    due_time = db.DateTimeProperty()

class OptionModel(db.Model):
    question_ref = db.ReferenceProperty(QuestionModel)
    text = db.StringProperty(required=True)

class OptionUserMapModel(db.Model):
    user = db.ReferenceProperty(UserModel, required=True)
    option = db.ReferenceProperty(OptionModel, required=True)
    
   
#    order = db.IntegerProperty(required=True)

#    name = db.StringProperty(required=True)
#    type = db.StringProperty(required=True, 
#                             choices=set(["cat", "dog", "bird"]))
#    birthdate = db.DateProperty()
#    weight_in_pounds = db.IntegerProperty()
#    spayed_or_neutered = db.BooleanProperty()
#    owner = db.UserProperty(required=True)
