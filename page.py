## ----------------------------------------------------------------------------
# import standard modules
import logging

# Google specific modules
from google.appengine.ext.db import djangoforms

# local modules
from models import Page
import webbase
import formbase

## ----------------------------------------------------------------------------

# Forms
class PageForm(djangoforms.ModelForm):
    class Meta:
        model = Page
        exclude = ['_class', 'content_html', 'owner', 'editor']

class List(webbase.WebBase):
    def get(self):
        pages = Page.all().order('-inserted')
        vals = {
            'title' : 'Section Layout List',
            'pages' : pages
        }
        self.template( 'admin-page-index.html', vals, 'admin' );

class FormHandler(formbase.FormBaseHandler):
    def type(self):
        return Page.__name__

    def form(self, *args, **kwargs):
        return PageForm(*args, **kwargs)

    def read_only_fields_edit(self):
        return ['name']

    # need to return something since otherwise 'name' won't be sent to the form
    def clean_name(self):
        if self.instance:
            return self.instance.name;
        else:
            return self.fields['name']

## ----------------------------------------------------------------------------
