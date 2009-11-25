## ----------------------------------------------------------------------------
# import standard modules
import re
import logging

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
        pages = models.Page.all().order('-inserted')
        vals = {
            'title' : 'Section Layout List',
            'pages' : pages
        }
        self.template( 'admin-page-index.html', vals, 'admin' );

# form
class FormHandler(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )

        vals = {
            'item' : item,
            'sections' : models.Section.all(),
            'types' : [ 'rst', 'phliky', 'text', 'code', 'html' ]
            }
        self.template( 'page-form.html', vals, 'admin' );

    def post(self):
        # some initial setup
        section = db.get( self.request.get('section') )

        # do some preprocessing of the input params
        name = self.request.get('name')
        if name == '':
            name = util.urlify(self.request.get('title'))

        attribute_raw = self.request.get('attribute_raw')

        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            item.section = section
            item.name = name
            item.title = self.request.get('title')
            item.content = self.request.get('content')
            item.type = self.request.get('type')
            item.label_raw = self.request.get('label_raw')
            item.attribute_raw = attribute_raw
        else:
            item = models.Page(
                section = section,
                name = name,
                title = self.request.get('title'),
                content = self.request.get('content'),
                type = self.request.get('type'),
                label_raw = self.request.get('label_raw'),
                attribute_raw = attribute_raw,
                )
        logging.info( 'here1=' + item.attribute_raw)
        item.set_derivatives()
        logging.info( 'here2=' + '|'.join(item.attribute) )
        item.put()
        self.redirect('.')

## ----------------------------------------------------------------------------
