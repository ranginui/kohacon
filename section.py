## ----------------------------------------------------------------------------
# import standard modules

# Google specific modules
from google.appengine.ext import db

# local modules
import models
import webbase
import formbase
import util

## ----------------------------------------------------------------------------

# list
class List(webbase.WebBase):
    def get(self):
        sections = models.Section.all()
        vals = {
            'title' : 'Section List',
            'sections' : sections
        }
        self.template( 'admin-section-index.html', vals, 'admin' );

# form
class FormHandler(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )

        vals = {
            'item' : item,
            'types' : models.type_choices,
            'layouts' : models.layout_choices,
            }
        self.template( 'section-form.html', vals, 'admin' );

    def post(self):
        # get all the incoming values
        path = self.request.get('path')
        title = self.request.get('title')
        description = self.request.get('description')
        type = self.request.get('type')
        layout = self.request.get('layout')

        # some pre-processing of the input params
        description_html = util.render(description, type)

        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            item.path = path
            item.title = title
            item.description = description
            item.description_html = description_html
            item.type = type
            item.layout = layout
        else:
            item = models.Section(
                path = path,
                title = title,
                description = description,
                description_html = description_html,
                type = type,
                layout = layout,
                )

        # put the item to the datastore
        item.put()
        self.redirect('.')

## ----------------------------------------------------------------------------
