## ----------------------------------------------------------------------------
# import standard modules
import logging
import re

# Google specific modules
from google.appengine.ext import db

# local modules
import models
import webbase
import formbase

## ----------------------------------------------------------------------------

# list
class List(webbase.WebBase):
    def get(self):
        images = models.Image.all().order('-inserted')
        vals = {
            'title' : ' List',
            'images' : images
        }
        self.template( 'admin-image-index.html', vals, 'admin' );

# form
class FormHandler(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            logging.info('item=' + item.__class__.__name__)

        vals = {
            'item' : item,
            'sections' : models.Section.all(),
            }
        self.template( 'image-form.html', vals, 'admin' );

    def post(self):
        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )

        # save the image
        file = self.request.POST['image']
        blah = file.value
        section = db.get( self.request.POST['section'] )
        imagedata = models.ImageData(
            data = self.request.POST.get('image').file.read()
            )
        imagedata.put()

        # remove the weirdness from the labels
        label = self.request.POST['label']
        label = re.sub('\r', '', label)

        # put the item to the stastore
        item = models.Image(
            section = section,
            name = self.request.POST['name'],
            title = self.request.POST['title'],
            filename = file.filename,
            mimetype = file.type,
            imagedata = imagedata,
            caption = self.request.POST['caption'],
            credit = self.request.POST['credit'],
            credit_link = self.request.POST['credit_link'],
            label = label.split('\n')
            )
        item.set_derivatives()
        item.put()
        self.redirect('.')

## ----------------------------------------------------------------------------
