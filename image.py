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
from models import Image
import webbase
import formbase
import util

## ----------------------------------------------------------------------------

# List
class List(webbase.WebBase):
    def get(self):
        images = Image.all().order('-inserted')
        vals = {
            'images' : images
        }
        self.template( 'image-list.html', vals, 'admin' );

# Edit
class Edit(webbase.WebBaseBlobstoreUploadHandler):
    def get(self):
        item = None
        if self.request.get('key'):
            item = Image.get( self.request.get('key') )

        vals = {
            'item'       : item,
            # this is either new.html or edit.html
            'upload_url' : blobstore.create_upload_url( str(urllib.unquote(self.request.path)) ),
            }
        self.template( 'image-form.html', vals, 'admin' );

    def post(self):
        item = None
        vals = {}

        # get all the incoming values
        title = self.request.get('title').strip()
        blob_key = None
        caption = self.request.get('caption').strip()
        credit_who = self.request.get('credit_who').strip()
        credit_link = self.request.get('credit_link').strip() if self.request.get('credit_link') else None
        label_raw = self.request.get('label_raw').strip()

        # get the file information
        uploaded_files = self.get_uploads('image')
        if len(uploaded_files) == 1:
            blob_info = uploaded_files[0]
            blob_key = blob_info.key()

        if self.request.get('key'):
            item = Page.get( self.request.get('key') )
            item.title       = title
            item.caption     = caption
            item.credit_who  = credit_who
            item.credit_link = credit_link
            item.label_raw   = label_raw
        else:
            item = Image(
                title       = title,
                caption     = caption,
                credit_who  = credit_who,
                credit_link = credit_link,
                label_raw   = label_raw,
                )

        if blob_key:
            item.blob = blob_key

        # update and save this page
        item.set_derivatives()
        item.put()
        self.redirect('.')

# Delete
class Del(webbase.WebBase):
    def get(self):
        try:
            if self.request.get('key'):
                item = Image.get( self.request.get('key') )

                vals = {
                    'item' : item,
                    }
                self.template( 'image-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        try:
            item = Image.get( self.request.get('key') ) if self.request.get('key') else None
            if item is not None:
                try:
                    if item.blob:
                        item.blob.delete()
                    item.delete()
                    self.redirect('.')
                except:
                    vals = {
                        'item' : item,
                        'err' : 'There was an error when deleting this image, please try again'
                        }
                    self.template( 'image-del.html', vals, 'admin' );
        except:
            self.redirect('.')

# ServeHandler
class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, filename):
        image = Image.all().filter('filename =', filename).get()
        if image:
            self.send_blob(image.blob)
        else:
            self.error(404)

## ----------------------------------------------------------------------------
