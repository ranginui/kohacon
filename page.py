## ----------------------------------------------------------------------------
# import standard modules
import re
import logging

# Google specific modules
from google.appengine.ext import db

# local modules
from models import Section, Page
import models
import webbase
import formbase
import util

## ----------------------------------------------------------------------------

# List
class List(webbase.WebBase):
    def get(self):
        pages = Page.all().order('-inserted')
        vals = {
            'title' : 'Section Layout List',
            'pages' : pages
        }
        self.template( 'page-list.html', vals, 'admin' );

# Edit
class Edit(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )

        vals = {
            'item' : item,
            'sections' : Section.all(),
            'types' : models.type_choices
            }
        self.template( 'page-form.html', vals, 'admin' );

    def post(self):
        item = None
        vals = {}
        try:
            # get all the incoming values
            section = db.get( self.request.get('section') )
            name = self.request.get('name').strip()
            title = self.request.get('title').strip()
            content = self.request.get('content')
            type = self.request.get('type')
            label_raw = self.request.get('label_raw').strip()
            attribute_raw = self.request.get('attribute_raw').strip()

            # some pre-processing of the input params
            if name == '':
                name = util.urlify(self.request.get('title'))

            if self.request.get('key'):
                item = db.get( self.request.get('key') )
                item.section = section
                item.name = name
                item.title = title
                item.content = content
                item.type = type
                item.label_raw = label_raw
                item.attribute_raw = attribute_raw
            else:
                item = Page(
                    section = section,
                    name = name,
                    title = title,
                    content = content,
                    type = type,
                    label_raw = label_raw,
                    attribute_raw = attribute_raw,
                    )

            # update and save this page
            item.set_derivatives()
            item.put()
            # once saved, regenerate certain section properties
            section.regenerate()
            self.redirect('.')
        except Exception, err:
            vals['item'] = self.request.POST
            vals['err'] = err
            vals['sections'] = Section.all()
            vals['types'] = models.type_choices
            self.template( 'page-form.html', vals, 'admin' );

# Delete
class Del(webbase.WebBase):
    def get(self):
        try:
            if self.request.get('key'):
                item = db.get( self.request.get('key') )

                vals = {
                    'item' : item,
                    }
                self.template( 'page-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        try:
            item = db.get( self.request.get('key') ) if self.request.get('key') else None
            if item is not None:
                try:
                    item.delete()
                    self.redirect('.')
                except:
                    vals = {
                        'item' : item,
                        'err' : 'There was an error when deleting this page, please try again'
                        }
                    self.template( 'page-del.html', vals, 'admin' );
        except:
            self.redirect('.')

## ----------------------------------------------------------------------------
