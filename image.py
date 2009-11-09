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
            # form = self.form(instance=item)
            # logging.info('form.instance=' + form.instance.__class__.__name__)
        else:
            # form = self.form()
            pass

        vals = {
            # 'type' : self.type(),
            # 'form' : form,
            'item' : item,
            'sections' : models.Section.all(),
            }
        self.template( 'image-form.html', vals, 'admin' );

    def post(self):
        item = None
        form = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            # form = self.form( self.request.POST, instance=item )
        else:
            # form = self.form( self.request.POST )
            pass

        # logging.info('Doing get() for ' + self.type() + ' with ' + (str(item.key()) or '[None]'))

        file = self.request.POST['image']
        logging.info('filename = ' + file.filename)
        logging.info('mimetype = ' + file.type)
        logging.info('length   = ' + str(len(file.value)))
        blah = file.value
        # section = models.Section.all().filter('key =', self.request.POST['section']).fetch(1)
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
