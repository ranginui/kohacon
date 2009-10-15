## ----------------------------------------------------------------------------
# import standard modules
import logging

# Google specific modules
from google.appengine.ext.db import djangoforms

# local modules
from models import Property
import webbase
import formbase
import config

## ----------------------------------------------------------------------------

# Forms
class PropertyForm(djangoforms.ModelForm):
    class Meta:
        model = Property
        exclude = ['owner', 'editor']

class List(webbase.WebBase):
    def get(self):
        properties = Property.all()
        vals = {
            'title' : 'Property List',
            'properties' : properties,
            'config' : config,
        }
        self.template( 'admin-property-index.html', vals, 'admin' );

class FormHandler(formbase.FormBaseHandler):
    def type(self):
        return Property.__name__

    def form(self, *args, **kwargs):
        return PropertyForm(*args, **kwargs)

## ----------------------------------------------------------------------------
