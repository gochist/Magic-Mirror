#from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from models import QuestionModel, OptionModel
import os

tpl_path = "template"

class MainHandler(webapp.RequestHandler):
    def get(self):
        query = QuestionModel.all().order('text')
        template_dict = {}
        template_dict['questions'] = query.fetch(10)
        ret = template.render(os.path.join(tpl_path, 'main.html'),
                              template_dict)
        self.response.out.write(ret)
            
class QuestionHandler(webapp.RequestHandler):
    def get(self, q_key):
        template_dict = {}
        question = QuestionModel.get(q_key)
        query = OptionModel.all()
        query.filter("question_ref = ", question)
        
        template_dict['options'] = query.fetch(10)
        template_dict['question'] = question
        ret = template.render(os.path.join(tpl_path, 'question.html'), template_dict)
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



def main():
    url_mapping = [('/', MainHandler),
                   ('/question.post', QuestionHandler),
                   ('/question/(.*)', QuestionHandler),
                   ]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
