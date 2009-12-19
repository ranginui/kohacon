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
import comment

sys.path.append('node')
import recipe

import migrate

## ----------------------------------------------------------------------------

class Home(webbase.WebBase):
    def get(self):
        self.redirect('/admin/section/')

class Delete(webbase.WebBase):
    def get(self):
        entity = db.get( self.request.get('key') )
        action = self.request.get('_act')
        if action == 'rem':
            pass
        elif action == 'del':
            entity.delete()
        else:
            pass
        vals = {
            'entity' : entity
            }
        self.template( 'delete.html', vals, 'admin' )

application = webapp.WSGIApplication(
    [
        ('/admin/', Home),

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
        ('/admin/image/new.html', image.FormHandler),
        ('/admin/image/edit.html', image.FormHandler),

        # files
        #('file/', file.FileList),
        #('file/edit.html', file.FileEdit),

        # comments
        ('/admin/comment/', comment.Index),

        # delete any entity
        ('/admin/del.html', Delete),

        # migrations
        ('/admin/migrate/', migrate.Migrate),
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
