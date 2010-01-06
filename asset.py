## ----------------------------------------------------------------------------
# import standard modules
import cgi
import urllib

# Google specific modules
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import blobstore

# local modules
import image
import file

## ----------------------------------------------------------------------------

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, key):
        key = str( urllib.unquote(key) )
        blob_info = blobstore.BlobInfo.get(key)
        if blob_info:
            self.send_blob(blob_info, save_as=True)
        else:
            self.error(404)

application = webapp.WSGIApplication(
    [
        ('/asset/([^/]+)', ServeHandler),
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
