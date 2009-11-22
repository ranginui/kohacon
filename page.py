## ----------------------------------------------------------------------------
# import standard modules
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
        label = re.sub('\r', '', self.request.get('label'))
        allow_comment = self.request.get('allow_comment', default_value='' )

        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )
            item.section = section
            item.name = name
            item.title = self.request.get('title')
            item.content = self.request.get('content')
            item.type = self.request.get('type')
            item.label = label.split('\n')
            item.allow_comment = True if allow_comment == 'Y' else False
        else:
            item = models.Page(
                section = section,
                name = name,
                title = self.request.get('title'),
                content = self.request.get('content'),
                type = self.request.get('type'),
                label = label.split('\n'),
                allow_comment = True if allow_comment == 'Y' else False,
                )
        item.set_derivatives()
        item.put()
        self.redirect('.')

## ----------------------------------------------------------------------------
