## ----------------------------------------------------------------------------
# import standard modules
import cgi
import os
from types import *

# Google specific modules
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# local modules
import webbase
import property
import section
import sectionlayout
import page
import image

## ----------------------------------------------------------------------------

class Home(webbase.WebBase):
    def get(self):
        vals = {
            'title' : 'Lollysite',
            'user' : users.get_current_user(),
            'app' : self
        }
        self.template( 'index.html', vals, 'admin' );

application = webapp.WSGIApplication(
    [
        ('/admin/', Home),

        # properties
        ('/admin/property/', property.List),
        ('/admin/property/new.html', property.FormHandler),

        # section layouts
        ('/admin/section-layout/', sectionlayout.SectionLayoutList),
        ('/admin/section-layout/new.html', sectionlayout.SectionLayoutNew),

        # sections
        ('/admin/section/', section.List),
        ('/admin/section/new.html', section.FormHandler),

        # pages
        ('/admin/page/', page.List),
        ('/admin/page/new.html', page.FormHandler),

        # images
        ('/admin/image/', image.List),
        ('/admin/image/new.html', image.FormHandler),

        # files
        #('file/', file.FileList),
        #('file/edit.html', file.FileEdit)
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
