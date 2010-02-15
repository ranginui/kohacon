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
import cgi
import datetime
import logging

# Google Specific
from google.appengine.ext.webapp import template
from django.template import Node

# local
from models import Node
import util

register = template.create_template_register()

## ----------------------------------------------------------------------------
# filters

# util.config_value() should never (usually?) raise an exception
def cfg(title):
    return util.config_value(title)

register.filter(cfg)

# takes an array and puts into separate lines (after making HTML safe)
def list(l):
    l = '\n'.join(l)
    return cgi.escape(l, True)

register.filter(list)

# takes a dict and returns the value of the item passed
def hash(h, key):
    if key in h:
        return h[key]
    else:
        return None

register.filter(hash)

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
