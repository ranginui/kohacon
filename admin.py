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
import sys
from types import *

# Google specific modules
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# local modules
import webbase
import property
import section
import page
import image
import file
import comment
import message

sys.path.append('node')
sys.path.append('admin')
import recipe
import load

import migrate

## ----------------------------------------------------------------------------

class Home(webbase.WebBase):
    def get(self):
        self.template( 'index.html', { 'title': 'Admin' }, 'admin' );

class Credit(webbase.WebBase):
    def get(self):
        self.template( 'credits.html', { 'title': 'Credits' }, 'admin' );

class Help(webbase.WebBase):
    def get(self, page):
        self.template( page, { 'title': 'Help' }, 'admin' );

application = webapp.WSGIApplication(
    [
        ('/admin/', Home),
        ('/admin/credits.html', Credit),

        # properties
        ('/admin/property/', property.List),
        ('/admin/property/new.html', property.Edit),
        ('/admin/property/edit.html', property.Edit),
        ('/admin/property/uncache.html', property.UnCache),
        ('/admin/property/del.html', property.Del),

        # sections
        ('/admin/section/', section.List),
        ('/admin/section/new.html', section.Edit),
        ('/admin/section/edit.html', section.Edit),
        ('/admin/section/del.html', section.Del),

        # pages
        ('/admin/page/', page.List),
        ('/admin/page/new.html', page.Edit),
        ('/admin/page/edit.html', page.Edit),
        ('/admin/page/del.html', page.Del),

        # recipes
        ('/admin/recipe/', recipe.List),
        ('/admin/recipe/new.html', recipe.Edit),
        ('/admin/recipe/edit.html', recipe.Edit),
        ('/admin/recipe/del.html', recipe.Del),

        # images
        ('/admin/image/', image.List),
        ('/admin/image/new.html', image.Edit),
        ('/admin/image/edit.html', image.Edit),
        ('/admin/image/del.html', image.Del),

        # files
        ('/admin/file/', file.List),
        ('/admin/file/new.html', file.Edit),
        ('/admin/file/edit.html', file.Edit),
        ('/admin/file/del.html', file.Del),

        # comments
        ('/admin/comment/', comment.Index),
        ('/admin/comment/del.html', comment.Del),
        ('/admin/comment/del-all.html', comment.DelAll),

        # messages
        ('/admin/message/', message.List),
        ('/admin/message/del.html', message.Del),

        # load
        ('/admin/load/', load.Import),

        # migrations
        ('/admin/migrate/', migrate.Migrate),

        # help
        ('/admin/(help-.*)', Help),
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
