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
import logging
import re
import urllib

# Google specific modules
from google.appengine.ext import db
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import blobstore

# local modules
from models import File
import webbase
import util

## ----------------------------------------------------------------------------

file_count = 20

# List
class List(webbase.WebBase):
    def get(self):
        files = File.all().order('-inserted').fetch(file_count+1)

        more = True if len(files) > file_count else False

        vals = {
            'files'      : files,
            'file_count' : file_count if more else len(files),
            'more'       : more,
        }
        self.template( 'file-list.html', vals, 'admin' );

# Edit
class Edit(webbase.WebBaseBlobstoreUploadHandler):
    def get(self):
        item = None
        if self.request.get('key'):
            item = File.get( self.request.get('key') )

        vals = {
            'item'       : item,
            # this is either new.html or edit.html
            'upload_url' : blobstore.create_upload_url( str(urllib.unquote(self.request.path)) ),
            }
        self.template( 'file-form.html', vals, 'admin' );

    def post(self):
        item = None
        vals = {}

        # get all the incoming values
        title = self.request.get('title').strip()
        blob_key = None
        label_raw = self.request.get('label_raw').strip()

        # get the file information
        uploaded_files = self.get_uploads('file')
        if len(uploaded_files) == 1:
            blob_info = uploaded_files[0]
            blob_key = blob_info.key()

        if self.request.get('key'):
            item = File.get( self.request.get('key') )
            item.title       = title
            item.label_raw   = label_raw
        else:
            item = File(
                title       = title,
                label_raw   = label_raw,
                )

        if blob_key:
            item.blob = blob_key

        # update and save this file
        item.set_derivatives()
        item.put()
        self.redirect('.')

# Delete
class Del(webbase.WebBase):
    def get(self):
        try:
            if self.request.get('key'):
                item = File.get( self.request.get('key') )

                vals = {
                    'item' : item,
                    }
                self.template( 'file-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        try:
            item = File.get( self.request.get('key') ) if self.request.get('key') else None
            if item is not None:
                try:
                    if item.blob:
                        item.blob.delete()
                    item.delete()
                    self.redirect('.')
                except:
                    vals = {
                        'item' : item,
                        'err' : 'There was an error when deleting this file, please try again'
                        }
                    self.template( 'file-del.html', vals, 'admin' );
        except:
            self.redirect('.')

# ServeHandler
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, filename):
        file = File.all().filter('filename =', filename).get()
        if file:
            self.send_blob(file.blob, save_as=True)
        else:
            self.error(404)

## ----------------------------------------------------------------------------
