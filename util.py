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

# AppEngine independent utils to help with any app

## ----------------------------------------------------------------------------
# import standard modules
import logging
import sys
import cgi
import re
import datetime
import re
import urllib

## ----------------------------------------------------------------------------
# Google specific modules
from google.appengine.api import memcache

## ----------------------------------------------------------------------------
# local modules

import textile
import markdown
import phliky
import models

## ----------------------------------------------------------------------------
# render the content as HTML

class InvalidTypeError(Exception):
    def __init__(self, type):
        self.type = type
    def __str__(self):
        return repr(type)

def esc(text):
    return cgi.escape(text, True)

def render(text, type):
    if type is None or type.strip() == '':
        return ''

    text = re.sub('\r', '', text);
    if type == 'html':
        return text

    elif type == 'text':
        html = ''
        paras = text.split('\n\n')
        for para in paras:
            html = html + '<p>' + esc(para) + '</p>\n'
        return html

    elif type == 'code':
        return '<pre>' + esc(text) + '</pre>\n'

    elif type == 'phliky':
        return phliky.text2html(text)

    elif type == 'textile':
        return textile.textile(text)

    elif type == 'markdown':
        return markdown.markdown(text)

    else:
        raise InvalidTypeError(type)

def urlify(title):
    name = title.lower()

    # special case to remove ' completely (for things like: let's it's and o'clock)
    name = re.sub(r'\'', '', name )

    # replace anything not a letter or number with a dash
    name = re.sub(r'[^a-z0-9]+', '-', name )

    # replace any dashes at start or end with one
    name = re.sub(r'-+', '-', name )
    name = re.sub(r'^-', '', name )

    # and multiple dashes with just one
    name = re.sub(r'-$', '', name )

    return name

def get_config():
    # query for the config
    query = models.Config.all()

    # make it if necessary
    config = None
    if query.count() == 0:
        config = models.Config()
        config.config = {}
        config.put()
        return None
    else:
        config = query.fetch(1)[0]

    return config

def config_value(title):
    # see if this 'title' config is in Memcache
    value = memcache.get(title, 'config')
    if value is not None:
        return value

    # get from the datastore
    config = get_config()

    # return it to the user
    if title in config.config:
        return config.config[title]
    else:
        return None

def construct_redirect(path):
    if path is None or path == '':
        path = '/'

    redirect = construct_url() + urllib.quote(path)
    return redirect

def construct_url():
    url = 'http://'
    if config_value('Sub Domain') is not None:
        url = url + config_value('Sub Domain') + '.'
    url = url + config_value('Naked Domain')
    return url

def str_to_datetime(str):
    """ takes strings of the form yyyy-mm-dd hh:mm:ss and returns a datetime """
    a = [ int(x) for x in re.split(r'[ \-:]', str) ]
    dt = datetime.datetime(a[0], a[1], a[2], a[3], a[4], a[5])
    return dt

def make_attr_raw_string(d):
    """ takes a dict and makes a string dependent on whether they are true """
    attr_raw = ''
    for attr in d.keys():
        if d[attr]:
            attr_raw = attr_raw + ' ' + attr
    attr_raw.strip()
    return attr_raw

## ----------------------------------------------------------------------------
