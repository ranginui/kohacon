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
from google.appengine.ext.db import polymodel
from google.appengine.api.labs.taskqueue import Task
from google.appengine.ext.blobstore import blobstore

# local stuff
import util
import properties

## ----------------------------------------------------------------------------

# all models should have the following properties:
# * owner = db.UserProperty( auto_current_user_add = True )
# * editor = db.UserProperty( auto_current_user = True )
# * inserted = db.DateTimeProperty( auto_now_add = True )
# * updated = db.DateTimeProperty( auto_now = True )

type_choices = ["text", "code", "phliky", "textile", "html", "markdown"]
node_choices = ['page', 'recipe']
layout_choices = ['content', 'blog', 'faq']

## ----------------------------------------------------------------------------
# normal models

# BaseModel
class BaseModel(db.Model):
    # common properties for _every_ datastore object
    owner = db.UserProperty( auto_current_user_add=True )
    editor = db.UserProperty( auto_current_user=True )
    inserted = db.DateTimeProperty( auto_now_add=True )
    updated = db.DateTimeProperty( auto_now=True )

# Property class so the application can be configured
class Property(BaseModel):
    title = db.StringProperty( required=True )
    value = db.StringProperty( required=True )

# Section: to group Nodes together
class Section(BaseModel):
    # path := usually something starting with '/', like '/', '/blog/', '/article/' and '/path/to/'
    # path := m{ / (a-z[a-z0-9]*/)* }xms # intial / followed by 0 or more sections
    path = db.StringProperty( required=True )
    title = db.StringProperty( required=True )
    description = db.TextProperty()
    type = db.StringProperty(required=True, choices=set(type_choices))
    layout = db.StringProperty(
        required=True,
        default='content',
        choices=layout_choices
        )
    attribute_raw = db.StringProperty( multiline=False )

    def has(self, attr):
        return [ x for x in self.attribute if x == attr ]

    # Derivative Properties
    description_html = db.TextProperty()
    attribute = db.StringListProperty()
    def set_derivatives(self):
        # set the description_html
        self.description_html = util.render(self.description, self.type)
        # set the lists from their raw values
        self.attribute = self.attribute_raw.split()

    # Generated Properties (and the tasks to kick them off)
    archive_json = properties.JsonProperty()
    label_json = properties.JsonProperty()
    def regenerate(self):
        Task( params={ 'key': str(self.key()) }, countdown=30, ).add( queue_name='section-regenerate' )

## ----------------------------------------------------------------------------
# polymodels

class Node(polymodel.PolyModel):
    # common properties for _every_ datastore object
    owner = db.UserProperty( auto_current_user_add=True )
    editor = db.UserProperty( auto_current_user=True )
    inserted = db.DateTimeProperty( auto_now_add=True )
    updated = db.DateTimeProperty( auto_now=True )

    # common properties for every Node
    section = db.ReferenceProperty( Section, required=True, collection_name='nodes' )
    # name := a-z[a-z0-9_-.]*
    name = db.StringProperty( required=True, multiline=False )
    title = db.StringProperty( required=True, multiline=False )
    label_raw = db.StringProperty( multiline=False )
    attribute_raw = db.StringProperty( multiline=False )

    # Derivative Properties
    label = db.StringListProperty()
    archive = db.StringListProperty()
    attribute = db.StringListProperty()
    def set_derivatives(self):
        # set the archive dates
        datetime = str(self.inserted)
        y = re.search(r'^(\d\d\d\d)', datetime, re.DOTALL | re.VERBOSE).group(1)
        m = re.search(r'^(\d\d\d\d-\d\d)', datetime, re.DOTALL | re.VERBOSE).group(1)
        d = re.search(r'^(\d\d\d\d-\d\d-\d\d)', datetime, re.DOTALL | re.VERBOSE).group(1)
        self.archive = [y, m, d]

        # set the lists from their raw values
        self.label = self.label_raw.split()
        self.attribute = self.attribute_raw.split()

    # Generated Properties (and the tasks to kick them off)
    comment_count = db.IntegerProperty( required=True, default=0 )
    def regenerate(self):
        Task( params={ 'key': str(self.key()) }, countdown=30, ).add( queue_name='node-regenerate' )

# Page
class Page(Node):
    content = db.TextProperty( required=False )
    type = db.StringProperty(required=True, choices=set(type_choices))

    # Derivative Properties
    content_html = db.TextProperty( required=False )

    def set_derivatives(self):
        Node.set_derivatives(self)
        self.content_html = util.render(self.content, self.type)

# Recipe
class Recipe(Node):
    intro = db.TextProperty( required=False )
    serves = db.StringProperty( required=False )
    ingredients = db.TextProperty( required=False )
    method = db.TextProperty( required=False )
    type = db.StringProperty(required=True, choices=set(type_choices))

    # Derivative Properties
    intro_html = db.TextProperty()
    ingredients_html = db.TextProperty()
    method_html = db.TextProperty()

    def set_derivatives(self):
        Node.set_derivatives(self)
        self.intro_html = util.render(self.intro, self.type)
        self.ingredients_html = util.render(self.ingredients, self.type)
        self.method_html = util.render(self.method, self.type)

# Files: See - http://blog.notdot.net/2009/9/Handling-file-uploads-in-App-Engine

## ----------------------------------------------------------------------------
# assets (BlobStore files)

class Asset(polymodel.PolyModel):
    # common properties for _every_ datastore object
    owner = db.UserProperty( auto_current_user_add=True )
    editor = db.UserProperty( auto_current_user=True )
    inserted = db.DateTimeProperty( auto_now_add=True )
    updated = db.DateTimeProperty( auto_now=True )

    # common properties for every Asset
    title = db.StringProperty( multiline=False )
    blob = blobstore.BlobReferenceProperty()
    label_raw = db.StringProperty( multiline=False )

    # Derivative Properties
    label = db.StringListProperty()
    filename = db.StringProperty( multiline=False )
    def set_derivatives(self):
        # set the lists from their raw values
        self.label = self.label_raw.split()
        if self.blob:
            self.filename = self.blob.filename

# Image
class Image(Asset):
    caption = db.TextProperty()
    credit_who = db.TextProperty()
    credit_link = db.LinkProperty()

# File
class File(Asset):
    pass

## ----------------------------------------------------------------------------
# comments

class Comment(BaseModel):
    node = db.ReferenceProperty( Node, required=True, collection_name='comments' )
    name = db.StringProperty(multiline=False)
    email = db.StringProperty(multiline=False)
    website = db.StringProperty(multiline=False)
    comment = db.TextProperty()
    status = db.StringProperty(
        required=True,
        default='new',
        choices=['new', 'approved', 'rejected']
        )

    # Derivative Properties
    comment_html = db.TextProperty()
    def set_derivatives(self):
        self.comment_html = util.render(self.comment, 'text')


## ----------------------------------------------------------------------------
# messages

class Message(BaseModel):
    type = db.StringProperty( multiline=False )
    subject = db.StringProperty( multiline=False )
    message = properties.JsonProperty()

## ----------------------------------------------------------------------------
