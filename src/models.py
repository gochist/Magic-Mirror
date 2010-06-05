from google.appengine.ext import db

class QuestionModel(db.Model):
    text = db.StringProperty(required=True)
    created_time = db.DateTimeProperty(auto_now_add=True)
    due_time = db.DateTimeProperty()

class OptionModel(db.Model):
    question_ref = db.ReferenceProperty(QuestionModel)
    text = db.StringProperty(required=True)    
    
class UserModel(db.Model):
    user_id = db.StringProperty(required=True)
    

   
#    order = db.IntegerProperty(required=True)

#    name = db.StringProperty(required=True)
#    type = db.StringProperty(required=True, 
#                             choices=set(["cat", "dog", "bird"]))
#    birthdate = db.DateProperty()
#    weight_in_pounds = db.IntegerProperty()
#    spayed_or_neutered = db.BooleanProperty()
#    owner = db.UserProperty(required=True)
