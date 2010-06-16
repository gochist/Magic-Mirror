from models import UserModel
import msg

class User(object):
    def __init__(self):
        self.loaded = False
        self.model = None
        
    def get_by_twit_id(self, twit_id):
        query = UserModel.all().filter("twit_id =", twit_id)
        count = query.count()
        if count == 1:
            self.loaded = True
            self.model = query.fetch(1)[0]
        else:
            self.loaded = False
            self.model = None
            
        if count > 1:
            msg.warn(1, twit_id=twit_id)            

        return self.model

    def set(self, twit_id, twit_screen_name, twit_img_url, time_zone,
            utc_offset):
        """set user information into DB
        
        Args: 
          twit_id:
          twit_screen_name:
          twit_img_url:
          time_zone:
          utc_offset:
        """
        model = self.get_by_twit_id(twit_id)
        if model: # when data already exists  
            model.twit_id = twit_id
            model.twit_screen_name = twit_screen_name
            model.twit_img_url = twit_img_url
            model.time_zone = time_zone
            model.utc_offset = utc_offset
            model.put()
        else :  # when data is not there
            model = UserModel(twit_id=twit_id,
                              twit_screen_name=twit_screen_name,
                              twit_img_url=twit_img_url,
                              time_zone=time_zone,
                              utc_offset=utc_offset)
            model.put()
            
        self.model = model
        
        return self.model
        
            
