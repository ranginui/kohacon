## ----------------------------------------------------------------------------
# import standard modules
import logging

# Google specific modules
from google.appengine.ext import db
from google.appengine.api import memcache

# local modules
from models import Property
import webbase
import formbase
import config

## ----------------------------------------------------------------------------

# list
class List(webbase.WebBase):
    def get(self):
        properties = Property.all()
        vals = {
            'title' : 'Property List',
            'properties' : properties,
            'config' : config,
        }
        self.template( 'property-list.html', vals, 'admin' );


# form
class FormHandler(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )

        vals = {
            'item' : item,
            }
        self.template( 'property-form.html', vals, 'admin' );

    def post(self):
        # get all the incoming values
        title = self.request.get('title')
        value = self.request.get('value')

        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            item.title = title
            item.value = value
        else:
            item = Property(
                title = title,
                value = value,
                )
        item.put()
        memcache.delete(title, namespace='property')
        self.redirect('.')

# Empty Form (ie. never seen ... does something then goes back to the PropertyList)
class UnCache(webbase.WebBase):
    def get(self):
        title = self.request.get('title')
        memcache.delete(title, namespace='property')
        self.redirect('.')

## ----------------------------------------------------------------------------
