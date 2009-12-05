## ----------------------------------------------------------------------------
# import standard modules
import cgi
import os
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

import migrate

## ----------------------------------------------------------------------------

class Home(webbase.WebBase):
    def get(self):
        vals = {
            'title' : 'Lollysite',
            'user' : users.get_current_user(),
            'app' : self
        }
        self.template( 'index.html', vals, 'admin' );

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
        ('/admin/property/new.html', property.FormHandler),
        ('/admin/property/edit.html', property.FormHandler),

        # sections
        ('/admin/section/', section.List),
        ('/admin/section/new.html', section.FormHandler),
        ('/admin/section/edit.html', section.FormHandler),

        # pages
        ('/admin/page/', page.List),
        ('/admin/page/new.html', page.FormHandler),
        ('/admin/page/edit.html', page.FormHandler),

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
