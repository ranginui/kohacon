## ----------------------------------------------------------------------------
# import standard modules
import cgi
import os
import logging
import re
import urllib

# Google specific modules
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import mail

# local modules
import webbase

## ----------------------------------------------------------------------------

class KohaCon(webbase.WebBase):
    def get(self):
        self.template( 'index.html', {}, 'discoverer' );

## ----------------------------------------------------------------------------

application = webapp.WSGIApplication(
    [
        ('/.*', KohaCon)
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
