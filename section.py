## ----------------------------------------------------------------------------
# import standard modules
import logging

# Google specific modules
from google.appengine.ext.db import djangoforms

# local modules
from models import Section
import webbase
import formbase

## ----------------------------------------------------------------------------

# Forms
class SectionForm(djangoforms.ModelForm):
    class Meta:
        model = Section
        exclude = ['owner', 'editor']

class List(webbase.WebBase):
    def get(self):
        sections = Section.all()
        vals = {
            'title' : 'Section List',
            'sections' : sections
        }
        self.template( 'admin-section-index.html', vals, 'admin' );

class FormHandler(formbase.FormBaseHandler):
    def type(self):
        return Section.__name__

    def form(self, *args, **kwargs):
        return SectionForm(*args, **kwargs)

## ----------------------------------------------------------------------------
