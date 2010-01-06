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
            recipes = Recipe.all().filter('section =', section).order('-inserted')
        else:
            recipes = Recipe.all().order('-inserted')

        vals = {
            'title'    : 'Recipe List',
            'sections' : Section.all(),
            'section'  : section,
            'recipes'    : recipes,
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
