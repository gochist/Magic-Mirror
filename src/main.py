from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from handlers import *

template.register_template_library('mirror_filters')

def main():
    url_mapping = [('/', MainHandler),
                   ('/home', HomeHandler),
                   ('/([0-9]*)', GameViewHandler),
                   ('/oauth/twitter/signin', TwitSigninHandler),
                   ('/oauth/twitter/signout', TwitSignoutHandler),
                   ('/oauth/twitter/callback', TwitCallbackHandler),
                   ('/game/(new|modify|delete)', GameHandler),
                   ('/game', GameHandler),
                   ('/timeline', TimelineHandler),
                   ('/test', TestHandler)
                   ]
    application = webapp.WSGIApplication(url_mapping, debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
