## ----------------------------------------------------------------------------
# import standard modules
import logging
import re

# Google specific modules
from google.appengine.ext import db

# local modules
from models import Section, Image, ImageData
import webbase
import formbase
import util

## ----------------------------------------------------------------------------

# list
class List(webbase.WebBase):
    def get(self):
        images = Image.all().order('-inserted')
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
            item = Image.get( self.request.get('key') )
            logging.info('item=' + item.__class__.__name__)

        vals = {
            'item' : item,
            'sections' : Section.all(),
            }
        self.template( 'image-form.html', vals, 'admin' );

    def post(self):
        item = None
        if self.request.get('key'):
            item = Image.get( self.request.get('key') )

        # do some preprocessing of the input params
        name = self.request.get('name')
        if name == '':
            name = util.urlify(self.request.get('title'))

        # save the image
        file = self.request.POST['image']
        section = Section.get( self.request.POST['section'] )
        imagedata = ImageData(
            data = self.request.POST.get('image').file.read()
            )
        imagedata.put()

        # put the item to the stastore
        item = Image(
            section = section,
            name = name,
            title = self.request.POST['title'],
            filename = file.filename,
            mimetype = file.type,
            imagedata = imagedata,
            caption = self.request.POST['caption'],
            credit = self.request.POST['credit'],
            credit_link = self.request.POST['credit_link'],
            label_raw = self.request.get('label_raw'),
            )

        # update and save this page
        item.set_derivatives()
        item.put()

        # once saved, regenerate certain section properties
        section.regenerate()

        self.redirect('.')

## ----------------------------------------------------------------------------
