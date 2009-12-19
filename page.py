## ----------------------------------------------------------------------------
# import standard modules
import re
import logging

# Google specific modules
from google.appengine.ext import db
from google.appengine.api.labs.taskqueue import Task
from google.appengine.api.datastore_errors import BadKeyError

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
        section = None
        if self.request.get('section'):
            try:
                section = Section.get( self.request.get('section') )
            except BadKeyError:
                # invalid key
                self.redirect('.')
            pages = Page.all().filter('section =', section).order('-inserted')
        else:
            pages = Page.all().order('-inserted')

        vals = {
            'title'    : 'Page List',
            'sections' : Section.all(),
            'section'  : section,
            'pages'    : pages,
        }
        self.template( 'page-list.html', vals, 'admin' );

# Edit
class Edit(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = Page.get( self.request.get('key') )

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
            section = Section.get( self.request.get('section') )
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
                item = Page.get( self.request.get('key') )
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
            # also, check that this section doesn't have duplicate content
            Task( params={ 'key': str(section.key()), 'name': item.name }, countdown=30, ).add( queue_name='section-check-duplicate-nodes' )
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
                item = Page.get( self.request.get('key') )

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
            item = Page.get( self.request.get('key') ) if self.request.get('key') else None
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
