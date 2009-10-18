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
        exclude = ['_class', 'owner', 'editor']

    # override the constructor so we can set some things read only
    # From: http://stackoverflow.com/questions/324477/in-a-django-form-how-to-make-a-field-readonly-or-disabled-so-that-it-cannot-be
    #def __init__(self, *args, **kwargs):
    #    super(PageForm, self).__init__(*args, **kwargs)
    #    instance = getattr(self, 'instance', None)
    #    logging.info('instance = ' + str(instance))
    #    # logging.warn(instance)
    #    if instance and instance.key:
    #        for field in ['name']:
    #            logging.warn('Setting ' + field + ' to readonly')
    #            self.fields[field].widget.attrs['readonly'] = True
                
    #def clean_name(self):
    #    if self.instance:
    #        logging.info('here')
    #        return self.instance.name;
    #    else:
    #        logging.info('there=' + str(self.fields['name']))
    #        return self.fields['name']

    #def clean_sku(self):
    #    instance = getattr(self, 'instance', None)
    #    if instance:
    #        return instance.name
    #    else:
    #        return self.cleaned_data.get('name', None)

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
