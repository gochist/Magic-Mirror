from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import urlfetch
from models import QuestionModel, OptionModel

import os
import config
import oauth2 as oauth

class AuthHandler(webapp.RequestHandler):
    def get(self, service, mode):
        if service == 'twitter':
            if mode == 'signin':
                consumer = oauth.Consumer(key=config.twit_app_key,
                                          secret=config.twit_app_secret)
                client = oauth.Client(consumer)
                resp, content = client.request('https://api.twitter.com/oauth/request_token', 'GET')
                self.response.out.write(content)
                self.response.out.write(resp)
                
                
#                self.redirect('http')
        
        

class MainHandler(webapp.RequestHandler):
    def get(self):
        query = QuestionModel.all().order('created_time')
        template_dict = {}
        template_dict['questions'] = query.fetch(10)
        ret = template.render(os.path.join(config.tpl_path, 'main.html'),
                              template_dict)
        self.response.out.write(ret)
            
class QuestionHandler(webapp.RequestHandler):
    @login_required
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

