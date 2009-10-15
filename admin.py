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
import section
import sectionlayout
import page
import property

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
        ('/', Home),

        # properties
        ('/admin/property/', property.List),
        ('/admin/property/new.html', property.FormHandler),
        ('/admin/property/edit.html', property.FormHandler),

        # section layouts
        ('/admin/section-layout/', sectionlayout.SectionLayoutList),
        ('/admin/section-layout/new.html', sectionlayout.SectionLayoutNew),
        ('/admin/section-layout/edit.html', sectionlayout.SectionLayoutEdit),

        # sections
        ('/admin/section/', section.List),
        ('/admin/section/new.html', section.FormHandler),
        ('/admin/section/edit.html', section.FormHandler),

        # pages
        ('/admin/page/', page.List),
        ('/admin/page/new.html', page.FormHandler),
        ('/admin/page/edit.html', page.FormHandler),

        # images
        #('image/', image.ImageList),
        #('image/edit.html', image.ImageEdit),

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
