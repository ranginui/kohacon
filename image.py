## ----------------------------------------------------------------------------
# import standard modules
import logging

# Google specific modules
from google.appengine.ext.webapp import template
from google.appengine.ext import db

# local modules
import models
import webbase
import formbase

## ----------------------------------------------------------------------------

# Forms
class List(webbase.WebBase):
    def get(self):
        images = models.Image.all().order('-inserted')
        vals = {
            'title' : ' List',
            'images' : images
        }
        self.template( 'admin-image-index.html', vals, 'admin' );

class FormHandler(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            logging.info('item=' + item.__class__.__name__)
        else:
            pass

        vals = {
            'item' : item,
            'sections' : models.Section.all(),
            }
        self.template( 'image-form.html', vals, 'admin' );

    def post(self):
        item = None
        form = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
        else:
            pass

        # save the image
        file = self.request.POST['image']
        logging.info('filename = ' + file.filename)
        logging.info('mimetype = ' + file.type)
        logging.info('length   = ' + str(len(file.value)))
        blah = file.value
        section = db.get( self.request.POST['section'] )
        imagedata = models.ImageData(
            data = self.request.POST.get('image').file.read()
            )
        imagedata.put()
        item = models.Image(
            section = section,
            name = self.request.POST['name'],
            title = self.request.POST['title'],
            filename = file.filename,
            mimetype = file.type,
            imagedata = imagedata,
            )
        item.put()
        self.redirect('.')

## ----------------------------------------------------------------------------
