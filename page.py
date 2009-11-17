## ----------------------------------------------------------------------------
# import standard modules
import logging
import re

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
            logging.info('item=' + item.__class__.__name__)

        vals = {
            'item' : item,
            'sections' : models.Section.all(),
            'types' : [ 'rst', 'phliky', 'text', 'code', 'html' ]
            }
        logging.info(item.section.key())
        self.template( 'page-form.html', vals, 'admin' );

    def post(self):
        # some initial setup
        section = db.get( self.request.get('section') )

        # remove the weirdness from the labels
        label = re.sub('\r', '', self.request.get('label'))
        allow_comment = self.request.get('allow_comment', default_value='' )

        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            item.section = section
            item.name = self.request.get('name')
            item.title = self.request.get('title')
            item.content = self.request.get('content')
            item.content_html = util.render(self.request.get('content'), self.request.get('type'))
            item.type = self.request.get('type')
            item.label = label.split('\n')
            item.allow_comment = True if allow_comment == 'Y' else False
        else:
            # put the item to the stastore
            item = models.Page(
                section = section,
                name = self.request.get('name'),
                title = self.request.get('title'),
                content = self.request.get('content'),
                content_html = util.render(self.request.get('content'), self.request.get('type')),
                type = self.request.get('type'),
                label = label.split('\n'),
                allow_comment = True if allow_comment == 'Y' else False,
                )

        item.put()
        self.redirect('.')

## ----------------------------------------------------------------------------
