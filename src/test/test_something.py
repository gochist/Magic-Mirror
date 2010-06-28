import unittest
from google.appengine.ext import webapp
from handler import *

class IndexTest(unittest.TestCase):

    def setUp(self):
        pass
#        self.application = webapp.WSGIApplication([('/', index.IndexHandler)], debug=True)
    
#    def test_default_page(self):
#        app = TestApp(self.application)
#        response = app.get('/')
#        self.assertEqual('200 OK', response.status)
#        self.assertTrue('Hello, World!' in response)
#    
#    def test_page_with_param(self):
#        app = TestApp(self.application)
#        response = app.get('/?name=Bob')
#        self.assertEqual('200 OK', response.status)
#        self.assertTrue('Hello, Bob!' in response)

    def test_test(self):
        self.assertFalse(True)