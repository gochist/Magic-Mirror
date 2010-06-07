from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
#from google.appengine.ext.webapp.util import login_required
from models import QuestionModel, OptionModel
import config, os
from oauth import OAuthClient
from util import twit_login_required


class MainHandler(webapp.RequestHandler):
    def get(self):
        client = OAuthClient('twitter', self)
        
        query = QuestionModel.all().order('created_time')
        template_dict = {}        
        template_dict['user'] = client.get_cookie()                
        template_dict['questions'] = query.fetch(10)
        
        if template_dict['user']:
            info = client.get('/account/verify_credentials')
            template_dict['profile_image_url'] = info['profile_image_url']
        
        ret = template.render(os.path.join(config.tpl_path, 'main.html'),
                              template_dict)
        self.response.out.write(ret)
            
class QuestionHandler(webapp.RequestHandler):
    @twit_login_required
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
        try:
            q_model = QuestionModel(text=question)
            q_model.put()
            for option in options.strip().splitlines():
                o_model = OptionModel(question_ref=q_model,
                                      text=option)
                o_model.put()
            
        except Exception:
            return
               
        self.redirect('/')
        

class OAuthHandler(webapp.RequestHandler):
    def get(self, service, action=''):
        if service not in config.OAUTH_APP_SETTINGS:
            return self.response.out.write(
                "Unknown OAuth Service Provider: %r" % service
                )

        client = OAuthClient(service, self)
        if action in client.__public__:
            self.response.out.write(getattr(client, action)())
        else:
            self.response.out.write(client.login())        
