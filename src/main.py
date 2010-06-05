#from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from handlers import MainHandler, QuestionHandler, AuthHandler

def main():
    url_mapping = [('/', MainHandler),
                   ('/auth/(.*)/(.*)', AuthHandler),
                   ('/question', QuestionHandler),
                   ('/question/(.*)', QuestionHandler),
                   ]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
