## ----------------------------------------------------------------------------
# import standard modules
import logging

# Google specific modules
from google.appengine.ext import db

# local modules
import webbase

## ----------------------------------------------------------------------------

# FormBaseHandler
class FormBaseHandler(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            logging.info('item=' + item.__class__.__name__)
            form = self.form(instance=item)
            logging.info('form.instance=' + form.instance.__class__.__name__)
        else:
            form = self.form()
        # logging.info('Doing get() for ' + self.type() + ' with ' + (str(item.key()) or '[None]'))
        vals = {
            'type' : self.type(),
            'form' : form,
            'item' : item,
            }
        self.template( 'admin-edit.html', vals, 'admin' );

    def post(self):
        item = None
        form = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            form = self.form( self.request.POST, instance=item )
        else:
            form = self.form( self.request.POST )
            
        # logging.info('Doing get() for ' + self.type() + ' with ' + (str(item.key()) or '[None]'))

        if form.is_valid():
            item = form.save( commit = False )
            item.put()
            self.redirect('.')
        else:
            vals = {
                'type' : self.type(),
                'form' : form,
                'item' : item,
                }
            self.template( 'admin-edit.html', vals, 'admin' );

class FormDelBase(webbase.WebBase):
    def get(self):
        return ''

## ----------------------------------------------------------------------------
