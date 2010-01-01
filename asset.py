## ----------------------------------------------------------------------------
# import standard modules
import cgi

# Google specific modules
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# local modules
import image
import file

## ----------------------------------------------------------------------------

application = webapp.WSGIApplication(
    [
        ('/asset/image/([^/]+)', image.ServeHandler),
        ('/asset/file/([^/]+)', file.ServeHandler),
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
