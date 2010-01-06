## ----------------------------------------------------------------------------
# import standard modules
import cgi
import datetime
import logging

# Google Specific
from google.appengine.ext.webapp import template
from django.template import Node

# local
import config
from models import Node

register = template.create_template_register()

## ----------------------------------------------------------------------------
# filters

# config.value should never (usually?) raise an exception
def cfg(title):
    return config.value(title)

register.filter(cfg)

# takes an array and puts into separate lines (after making HTML safe)
def list(l):
    l = '\n'.join(l)
    return cgi.escape(l, True)

register.filter(list)

# finds the latest 'x' number of nodes in a particular section
def latest(section, limit):
    nodes_query = Node.all().filter('section =', section.key()).order('-inserted')
    nodes = None
    if limit > 0:
        nodes = nodes_query.fetch(limit)
    return nodes or nodes_query

register.filter(latest)

# finds all the nodes in a section (forwards)
def all(section):
    nodes_query = Node.all().filter('section =', section.key()).order('inserted')
    return nodes_query

register.filter(all)

# finds the 'index' page of this section
def index(section):
    # have to return an iterable (since I have no idea how to assign it to one var in the template)
    nodes = Node.all().filter('section =', section.key()).filter('name =', 'index')
    return nodes

register.filter(index)

# returns whether this entity has a particular attribute
def has(item, attribute):
    # loop through the entities
    for a in item.attribute:
        if a == attribute:
            return True
    return False

register.filter(has)

## ----------------------------------------------------------------------------
