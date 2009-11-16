## ----------------------------------------------------------------------------
# Google specific modules
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

# local stuff
import derivedproperty
import util

## ----------------------------------------------------------------------------

# all models should have the following properties:
# * owner = db.UserProperty( auto_current_user_add = True )
# * editor = db.UserProperty( auto_current_user = True )
# * inserted = db.DateTimeProperty( auto_now_add = True )
# * updated = db.DateTimeProperty( auto_now = True )

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
class Section(BaseModel):
    # path := usually something starting with '/', like '/', '/blog/', '/article/' and '/path/to/'
    # path := m{ / (a-z[a-z0-9]*/)* }xms # intial / followed by 0 or more sections
    path = db.StringProperty( required=False )
    title = db.StringProperty( required=True )
    description = db.TextProperty()

    # so it looks nice in References in DjangoForms
    def __unicode__(self):
        return self.title

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
    label = db.StringListProperty()
    allow_comment = db.BooleanProperty( required=True, default=True )

# Page
class Page(Node):
    content = db.TextProperty( required=True )
    type = db.StringProperty(required=True, choices=set(["text", "phliky", "rst", "html"]))

    @derivedproperty.DerivedProperty
    def content_html(self):
        return util.render(self.content, self.type)

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
