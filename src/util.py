from google.appengine.ext import webapp
#from oauth import OAuthClient

def twit_login_required(handler_method):
    """A decorator to require that a user be logged in to access a handler.
    
    To use it, decorate your get() method like this:
    
      @login_required
      def get(self):
        user = users.get_current_user(self)
        self.response.out.write('Hello, ' + user.nickname())
    
    We will redirect to a login page if the user is not logged in. We always
    redirect to the request URI, and Google Accounts only redirects back as a GET
    request, so this should not be used for POSTs.
    """
#    def check_login(self, *args):
#        if self.request.method != 'GET':
#            raise webapp.Error('The check_login decorator can only be used for GET '
#                               'requests')
#        client = OAuthClient('twitter', self)
#        user = client.get_cookie()
#        if not user:
#            self.redirect("/oauth/twitter/login")
##            self.redirect(users.create_login_url(self.request.uri))
#            return
#        else:
#            handler_method(self, *args)     
    return
