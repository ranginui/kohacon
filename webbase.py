## ----------------------------------------------------------------------------
# Lollysite is a website builder and blogging platform for Google App Engine.
#
# Copyright (c) 2009, 2010 Andrew Chilton <andy@chilts.org>.
#
# Homepage  : http://www.chilts.org/project/lollysite/
# Ohloh     : https://www.ohloh.net/p/lollysite/
# FreshMeat : http://freshmeat.net/projects/lollysite
# Source    : http://gitorious.org/lollysite/
#
# This file is part of Lollysite.
#
# Lollysite is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Lollysite is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Lollysite.  If not, see <http://www.gnu.org/licenses/>.
#
## ----------------------------------------------------------------------------

# import standard modules
import cgi
import os
import logging

# Google specific
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
from google.appengine.ext.webapp import template

## ----------------------------------------------------------------------------

template.register_template_library('filter')

## ----------------------------------------------------------------------------

# WebBase
class WebBase(webapp.RequestHandler):
    def esc(self, s):
        return cgi.escape(s, True)

    def write(self, s):
        self.response.out.write(s + '\n');

    def template(self, template_filename, vals=None, theme=None):
        # should be config.theme instead of 'default'
        path = os.path.join(os.path.dirname(__file__), 'theme', (theme or 'default'), template_filename)

        # add some things in for every template to use
        vals['user'] = users.get_current_user()
        vals['app'] = self
        vals['url_login'] = users.create_login_url( self.request.uri )
        vals['url_logout'] = users.create_logout_url( self.request.uri )

        self.write( template.render(path, vals or {}) )

# WebBaseBlobstoreUploadHandler
class WebBaseBlobstoreUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def write(self, s):
        self.response.out.write(s + '\n');

    def template(self, template_filename, vals=None, theme=None):
        # should be config.theme instead of 'default'
        path = os.path.join(os.path.dirname(__file__), 'theme', (theme or 'default'), template_filename)

        # add some things in for every template to use
        vals['user'] = users.get_current_user()
        vals['app'] = self
        vals['url_login'] = users.create_login_url( self.request.uri )
        vals['url_logout'] = users.create_logout_url( self.request.uri )

        self.write( template.render(path, vals or {}) )

## ----------------------------------------------------------------------------
