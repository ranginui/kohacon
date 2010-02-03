## ----------------------------------------------------------------------------
# Lollysite is a website builder and blogging platform for Google App Engine.
#
# Copyright (c) 2009, 2010 Andrew Chilton <andy@chilts.org>.
#
# Homepage  : http://www.chilts.org/project/lollysite/
# Ohloh     : https://www.ohloh.net/p/lollysite/
# FreshMeat : http://freshmeat.net/projects/lollysite
# Source    : http://gitorious.org/lollysite/
#
# This file is part of Lollysite.
#
# Lollysite is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Lollysite is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Lollysite.  If not, see <http://www.gnu.org/licenses/>.
#
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
import util

## ----------------------------------------------------------------------------

page_count = 20

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
            pages = Page.all().filter('section =', section).order('-inserted').fetch(page_count+1)
        else:
            pages = Page.all().order('-inserted').fetch(page_count+1)

        more = True if len(pages) > page_count else False

        vals = {
            'title'      : 'Page List',
            'sections'   : Section.all(),
            'section'    : section,
            'pages'      : pages,
            'page_count' : page_count if more else len(pages),
            'more'       : more,
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
            attribute_raw = util.make_attr_raw_string(
                {
                    'index-entry'   : self.request.get('index_entry'),
                    'has-comments'  : self.request.get('has_comments'),
                    'comments-open' : self.request.get('comments_open'),
                    }
                ).strip()

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
            Task( params={ 'section_key': str(section.key()), 'name': item.name }, countdown=30, ).add( queue_name='section-check-duplicate-nodes' )
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
