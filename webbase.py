## ----------------------------------------------------------------------------
# import standard modules
import cgi
import os
import logging

# Google specific
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template

## ----------------------------------------------------------------------------

# the local classes
class WebBase(webapp.RequestHandler):
    def esc(self, s):
        return cgi.escape(s, True)

    def write(self, s):
        self.response.out.write(s + '\n');

    def template(self, template_filename, vals=None, theme=None):
        #logging.info('theme=' + theme);
        #logging.info('template=' + template_filename);
        # should be config.theme instead of 'default'
        path = os.path.join(os.path.dirname(__file__), 'theme', (theme or 'default'), template_filename)
        logging.info('path=' + path);

        # add some things in for every template to use
        vals['user'] = users.get_current_user()
        vals['app'] = self
        vals['url_login'] = users.create_login_url( self.request.uri )
        vals['url_logout'] = users.create_logout_url( self.request.uri )

        self.write( template.render(path, vals or {}) )

## ----------------------------------------------------------------------------
