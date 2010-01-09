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
