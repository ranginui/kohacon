## ----------------------------------------------------------------------------
# import standard modules
import logging
import urllib

# Google specific modules
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

# local modules
from models import Image, File
import webbase

## ----------------------------------------------------------------------------

class Image(webbase.WebBase):
    def get(self, name):
        name = urllib.unquote(name)
        image = Image.all().filter('name =', name).fetch(1)[0]

        self.response.headers['Content-Type'] = image.mimetype
        self.response.out.write(image.imagedata.data)

class File(webbase.WebBase):
    def get(self):
        path = urllib.unquote(self.request.path)
        file = File.all().filter('name =', name).fetch(1)[0]

        self.response.headers['Content-Type'] = file.mimetype
        self.response.out.write(file.filedata.data)

## ----------------------------------------------------------------------------

application = webapp.WSGIApplication(
    [
        ('/node/image/(.*)', Image),
        ('/node/file/(.*)', File),
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
