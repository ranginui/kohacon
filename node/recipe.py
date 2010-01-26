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
import sys

# Google specific modules
from google.appengine.ext import db
from google.appengine.api.labs.taskqueue import Task
from google.appengine.api.datastore_errors import BadKeyError

# local modules
sys.path.append("..")
from models import Section, Recipe
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
            recipes = Recipe.all().filter('section =', section).order('-inserted').fetch(page_count+1)
        else:
            recipes = Recipe.all().order('-inserted').fetch(page_count+1)

        more = True if len(recipes) > page_count else False

        vals = {
            'title'      : 'Recipe List',
            'sections'   : Section.all(),
            'section'    : section,
            'recipes'    : recipes,
            'page_count' : page_count if more else len(recipes),
            'more'       : more,
        }
        self.template( 'recipe-list.html', vals, 'admin' );

# Edit
class Edit(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = Recipe.get( self.request.get('key') )

        vals = {
            'item' : item,
            'sections' : Section.all(),
            'types' : models.type_choices
            }
        self.template( 'recipe-form.html', vals, 'admin' );

    def post(self):
        item = None
        vals = {}
        try:
            # get all the incoming values
            section = Section.get( self.request.get('section') )
            name = self.request.get('name').strip()
            title = self.request.get('title').strip()
            intro = self.request.get('intro')
            serves = self.request.get('serves')
            ingredients = self.request.get('ingredients')
            method = self.request.get('method')
            type = self.request.get('type')
            label_raw = self.request.get('label_raw').strip()
            attribute_raw = self.request.get('attribute_raw').strip()

            # some pre-processing of the input params
            if name == '':
                name = util.urlify(self.request.get('title'))

            if self.request.get('key'):
                item = Recipe.get( self.request.get('key') )
                item.section = section
                item.name = name
                item.title = title
                item.intro = intro
                item.serves = serves
                item.ingredients = ingredients
                item.method = method
                item.type = type
                item.label_raw = label_raw
                item.attribute_raw = attribute_raw
            else:
                item = Recipe(
                    section = section,
                    name = name,
                    title = title,
                    intro = intro,
                    serves = serves,
                    ingredients = ingredients,
                    method = method,
                    type = type,
                    label_raw = label_raw,
                    attribute_raw = attribute_raw,
                    )

            # update and save this recipe
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
            self.template( 'recipe-form.html', vals, 'admin' );

# Delete
class Del(webbase.WebBase):
    def get(self):
        try:
            if self.request.get('key'):
                item = Recipe.get( self.request.get('key') )

                vals = {
                    'item' : item,
                    }
                self.template( 'recipe-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        try:
            item = Recipe.get( self.request.get('key') ) if self.request.get('key') else None
            if item is not None:
                try:
                    item.delete()
                    self.redirect('.')
                except:
                    vals = {
                        'item' : item,
                        'err' : 'There was an error when deleting this recipe, please try again'
                        }
                    self.template( 'recipe-del.html', vals, 'admin' );
        except:
            self.redirect('.')

## ----------------------------------------------------------------------------
