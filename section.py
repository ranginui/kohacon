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
import logging

# Google specific modules
from google.appengine.ext import db
from google.appengine.api.labs.taskqueue import Task

# local modules
import models
from models import Section
import webbase
import util

## ----------------------------------------------------------------------------

section_count = 20

# List
class List(webbase.WebBase):
    def get(self):
        sections = Section.all().fetch(section_count+1)

        more = True if len(sections) > section_count else False

        vals = {
            'title'         : 'Section List',
            'sections'      : sections,
            'section_count' : section_count if more else len(sections),
            'more'          : more,
        }
        self.template( 'section-list.html', vals, 'admin' );

# Edit
class Edit(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = Section.get( self.request.get('key') )

        vals = {
            'item' : item,
            'types' : models.type_choices,
            'layouts' : models.layout_choices,
            }
        self.template( 'section-form.html', vals, 'admin' );

    def post(self):
        item = None
        vals = {}
        try:
            # get all the incoming values
            path = self.request.get('path').strip()
            title = self.request.get('title').strip()
            description = self.request.get('description')
            type = self.request.get('type')
            layout = self.request.get('layout')
            attribute_raw = util.make_attr_raw_string(
                {
                    'sitemap-entry' : self.request.get('sitemap_entry'),
                    'contact-form'  : self.request.get('contact_form'),
                    'sitefeed'      : self.request.get('sitefeed'),
                    }
                ).strip()

            # some pre-processing of the input params
            description_html = util.render(description, type)

            if self.request.get('key'):
                item = Section.get( self.request.get('key') )
                item.path = path
                item.title = title
                item.description = description
                item.description_html = description_html
                item.type = type
                item.layout = layout
                item.attribute_raw = attribute_raw
            else:
                item = Section(
                    path = path,
                    title = title,
                    description = description,
                    description_html = description_html,
                    type = type,
                    layout = layout,
                    attribute_raw = attribute_raw,
                    )

            # update and save this section
            item.set_derivatives()
            item.put()
            # once saved, add the section to the two task queues
            item.regenerate()
            self.redirect('.')
        except Exception, err:
            vals['item'] = self.request.POST
            vals['err'] = err
            vals['types'] = models.type_choices
            vals['layouts'] = models.layout_choices
            self.template( 'section-form.html', vals, 'admin' );

# Delete
class Del(webbase.WebBase):
    def get(self):
        try:
            if self.request.get('key'):
                item = Section.get( self.request.get('key') )

                vals = {
                    'item' : item,
                    }
                self.template( 'section-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        try:
            item = Section.get( self.request.get('key') ) if self.request.get('key') else None
            if item is not None:
                try:
                    item.delete()
                    self.redirect('.')
                except:
                    vals = {
                        'item' : item,
                        'err' : 'There was an error when deleting this section, please try again'
                        }
                    self.template( 'section-del.html', vals, 'admin' );
        except:
            self.redirect('.')

## ----------------------------------------------------------------------------
