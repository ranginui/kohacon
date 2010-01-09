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
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

# local modules
from models import Property

## ----------------------------------------------------------------------------

register = template.create_template_register()

# utility functions
def value(title):
    # see if this is in Memcache
    value = memcache.get(title, 'property')
    if value is not None:
        return value

    # not in Memcached, so ask the datastore
    data = Property.all().filter("title =", title)
    if not data.count():
        return ''

    # if this property has no value
    value = data[0].value
    if value is None:
        return ''

    # set the new value in memcache and return it
    memcache.set(title, value, namespace='property')
    return value

## ----------------------------------------------------------------------------
