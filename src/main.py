from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from handlers import *

template.register_template_library('mirror_filters')

def main():
    url_mapping = [('/', MainHandler),
                   ('/home', HomeHandler),
                   ('/home/(.*)', HomeHandler),
                   ('/([0-9]*)', GameViewHandler),
                   ('/([0-9]*)/(msg|delete)', GameViewHandler),
                   ('/msg/(.*)/delete', MsgDeleteHandler),
                   ('/([0-9]*)/([0-9]*)', GameJoinHandler),
                   ('/([0-9]*)/([0-9]*)/set_result', GameResultHandler),
                   ('/oauth/twitter/signin', TwitSigninHandler),
                   ('/oauth/twitter/signout', TwitSignoutHandler),
                   ('/oauth/twitter/callback', TwitCallbackHandler),
                   ('/game/(new)', GameHandler),
                   ('/game', GameHandler),
                   ('/user/(.*).json', UserHandler),
                   ('/error', ErrorHandler),
                   ('/ranking', RankingHandler),
                   ('/timeline', TimelineHandler),
#                   ('/temp', TestHandler),
                   ]
    application = webapp.WSGIApplication(url_mapping, debug=False)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
