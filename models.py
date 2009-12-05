## ----------------------------------------------------------------------------
# import standard modules
import re
import logging

# Google specific modules
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.api.labs.taskqueue import Task

# local stuff
import util
import properties

## ----------------------------------------------------------------------------

# all models should have the following properties:
# * owner = db.UserProperty( auto_current_user_add = True )
# * editor = db.UserProperty( auto_current_user = True )
# * inserted = db.DateTimeProperty( auto_now_add = True )
# * updated = db.DateTimeProperty( auto_now = True )

type_choices = ["text", "code", "phliky", "html"]
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

# SectionLayout: how to lay out each section
class SectionLayout(BaseModel):
    title = db.StringProperty( required=True )
    description = db.TextProperty()
    template = db.TextProperty( required=True )

    # so it looks nice in References in DjangoForms
    def __unicode__(self):
        return self.title

# Section: to group Nodes together
class Section(db.Model):
    # path := usually something starting with '/', like '/', '/blog/', '/article/' and '/path/to/'
    # path := m{ / (a-z[a-z0-9]*/)* }xms # intial / followed by 0 or more sections
    path = db.StringProperty( required=True )
    title = db.StringProperty( required=True )
    description = db.TextProperty()
    description_html = db.TextProperty()
    type = db.StringProperty(required=True, choices=set(type_choices))
    layout = db.StringProperty(
        required=False,
        default='content',
        choices=layout_choices
        )
    attribute_raw = db.StringProperty( multiline=False )

    # Derivative Properties
    attribute = db.StringListProperty()
    def set_derivatives(self):
        # set the lists from their raw values
        self.attribute = self.attribute_raw.split(' ')

    # Generated Properties (and the tasks to kick them off)
    archive_json = properties.JsonProperty()
    label_json = properties.JsonProperty()
    def regenerate(self):
        Task( params={ 'key': self.key }, countdown=30, ).add( queue_name='section-regenerate' )

# NodeLayout: how to lay out each node
class NodeLayout(BaseModel):
    title = db.StringProperty( required=True )
    description = db.TextProperty()
    template = db.TextProperty( required=True )

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
        self.label = self.label_raw.split(',')
        self.attribute = self.attribute_raw.split(r' ')

    # Generated Properties (and the tasks to kick them off)
    comment_count = db.IntegerProperty( required=True, default=0 )
    def regenerate(self):
        Task( params={ 'key': self.key }, countdown=30, ).add( queue_name='node-regenerate' )

# Page
class Page(Node):
    content = db.TextProperty( required=True )
    content_html = db.TextProperty()
    type = db.StringProperty(required=True, choices=set(type_choices))

    def set_derivatives(self):
        Node.set_derivatives(self)
        self.content_html = util.render(self.content, self.type)

# Files: See - http://blog.notdot.net/2009/9/Handling-file-uploads-in-App-Engine

# Image
class ImageData(db.Model):
    data = db.BlobProperty( required=True )

class Image(Node):
    caption = db.TextProperty()
    credit = db.TextProperty()
    credit_link = db.LinkProperty()
    imagedata = db.ReferenceProperty( ImageData, required=True, collection_name='image' )
    filename = db.StringProperty( required=True )
    mimetype = db.StringProperty( required=True )

# File
class FileData(db.Model):
    data = db.BlobProperty( required=True )

class File(Node):
    filedata = db.ReferenceProperty( FileData, required=True, collection_name='file' )
    filename = db.StringProperty( required=True )
    mimetype = db.StringProperty( required=True )

## ----------------------------------------------------------------------------
# comments

class Comment(BaseModel):
    node = db.ReferenceProperty( Node, required=True, collection_name='comments' )
    name = db.StringProperty(multiline=False)
    email = db.StringProperty(multiline=False)
    website = db.StringProperty(multiline=False)
    comment = db.TextProperty()
    comment_html = db.TextProperty()
    status = db.StringProperty(
        required=True,
        default='new',
        choices=['new', 'approved', 'rejected']
        )

## ----------------------------------------------------------------------------
