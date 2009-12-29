## ----------------------------------------------------------------------------
# import standard modules
import re
import logging
import sys
import yaml
import datetime

# Google specific modules
from google.appengine.ext import db
from google.appengine.api.labs.taskqueue import Task
from google.appengine.api.datastore_errors import BadKeyError
from django.utils import simplejson as json

# local modules
sys.path.append("..")
from models import Section, Page, Recipe, Comment
import models
import webbase
import formbase
import util

## ----------------------------------------------------------------------------

class Import(webbase.WebBase):
    def get(self):
        vals = {
            'sections'   : Section.all(),
            'node_types' : models.node_choices,
            'title'      : 'Import a node',
            'data_types' : [
                { 'value' : 'json', 'text' : 'JSON' },
                { 'value' : 'yaml', 'text' : 'YAML' },
                ],
            'node_type'   : self.request.get('node_type'),
            'section_key' : self.request.get('section_key'),
            'data_type'   : self.request.get('data_type'),
            }
        self.template( 'load-form.html', vals, 'admin' );

    def post(self):
        msgs = []
        section = None
        try:
            section = Section.get( self.request.get('section_key') )
        except BadKeyError:
            # invalid key, try again
            self.redirect('.')

        node_type = self.request.get('node_type')
        data_input = self.request.POST.get('data_input').file.read()
        data_type = self.request.get('data_type')

        data = None
        if data_type == 'json':
            data = json.loads( data_input )
        elif data_type == 'yaml':
            data = yaml.load( data_input )
        else:
            # someone is messing with the input params
            self.redirect('.')

        # logging.info( 'data=' + json.dumps( data ) )

        # figure out what this node_type is
        item = None
        if node_type == 'page':
            item = Page(
                section = section,
                name = data['name'],
                title = data['title'],
                content = data['content'],
                type = data['type'],
                label_raw = ' '.join( data['label'] ),
                attribute_raw = ' '.join( data['attribute'] ),
                inserted = util.str_to_datetime( data['inserted'] ),
                updated = util.str_to_datetime( data['updated'] ),
                )

        elif node_type == 'recipe':
            item = Recipe(
                section = section,
                name = data['name'],
                title = data['title'],
                intro = data['intro'],
                serves = data['serves'],
                ingredients = data['ingredients'],
                method = data['method'],
                type = data['type'],
                label_raw = ' '.join( data['label'] ),
                attribute_raw = ' '.join( data['attribute'] ),
                inserted = util.str_to_datetime( data['inserted'] ),
                updated = util.str_to_datetime( data['updated'] ),
                )

        else:
            # again, someone is messing with the input params
            self.redirect('.')

        # regenerate this item
        item.set_derivatives()
        item.put()
        item.section.regenerate()

        # output messages
        msgs.append( 'Added node [%s, %s]' % (item.name, item.title) )

        if 'comments' in data:
            for comment in data['comments']:
                # load each comment in against this node
                comment = Comment(
                    node = item,
                    name = comment['name'],
                    email = comment['email'],
                    website = comment['website'],
                    comment = comment['comment'],
                    comment_html = util.render(comment['comment'], 'text'),
                    status = comment['status'],
                    inserted = util.str_to_datetime( comment['inserted'] ),
                    updated = util.str_to_datetime( comment['updated'] ),
                )
                comment.put()
                msgs.append( 'Added comment [%s, %s]' % (comment.name, comment.email) )

        # now that we've added a node, regenerate it
        item.regenerate()

        # also, check that this section doesn't have duplicate content
        Task( params={ 'section_key': str(section.key()), 'name': item.name }, countdown=30, ).add( queue_name='section-check-duplicate-nodes' )

        vals = {
            'msgs'        : msgs,
            'node_type'   : node_type,
            'section_key' : section.key(),
            'data_type'   : data_type,
            }
        self.template( 'load-import.html', vals, 'admin' );

## ----------------------------------------------------------------------------
