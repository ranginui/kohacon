## ----------------------------------------------------------------------------
# import standard modules
#import cgi
#import os
#import logging

# Google specific
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import util

## ----------------------------------------------------------------------------

sample_text = """\
!1 Hello, World!

This is more
paras.

 Some <pre> here.

< Some
<em>html</em>
here.

" Quote here.

!2 The End

(Ends)
"""

class Rst(webapp.RequestHandler):
    def get(self):
        html = util.render('Hello *World*!', 'rst')
        self.response.out.write(html)

class Phliky(webapp.RequestHandler):
    def get(self):
        html = util.render(sample_text, 'phliky')
        self.response.out.write(html)

class Text(webapp.RequestHandler):
    def get(self):
        html = util.render(sample_text, 'text')
        self.response.out.write(html)

class Code(webapp.RequestHandler):
    def get(self):
        html = util.render(sample_text, 'code')
        self.response.out.write(html)

## ----------------------------------------------------------------------------

application = webapp.WSGIApplication(
    [
        ('/test/rst.html', Rst),
        ('/test/phliky.html', Phliky),
        ('/test/text.html', Text),
        ('/test/code.html', Code),
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
