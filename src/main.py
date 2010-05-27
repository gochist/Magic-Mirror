#from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import os

tpl_path = "template"

class MainHandler(webapp.RequestHandler):
    def get(self):
        template_dict = {}
        ret = template.render(os.path.join(tpl_path, 'main.html'),
                              template_dict)
        self.response.out.write(ret)
            
class QuestionHandler(webapp.RequestHandler):
    def post(self):
        question = self.request.get('question')
        options = self.request.get('options')
        self.response.out.write(question)      
        self.response.out.write(options)


url_mapping = [('/', MainHandler), 
               ('/question.post', QuestionHandler)]

application = webapp.WSGIApplication(url_mapping, debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()