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
from google.appengine.ext import db
from google.appengine.api import memcache

# local modules
from models import Config
import webbase
import util

## ----------------------------------------------------------------------------

# List
class List(webbase.WebBase):
    def get(self):
        config = util.get_config()
        vals = {
            'config' : config,
        }
        self.template( 'config-list.html', vals, 'admin' );

# Edit
class Edit(webbase.WebBase):
    def get(self):
        config = util.get_config()
        title = None
        value = None
        if self.request.get('title'):
            title = self.request.get('title')
            if title in config.config:
                value = config.config[title]

        vals = {
            'item'  : {
                'title' : title,
                'value' : value,
                }
            }
        self.template( 'config-form.html', vals, 'admin' );

    def post(self):
        title = None
        value = None
        config = util.get_config()
        try:
            # get all the incoming values
            title = self.request.get('title').strip()
            value = self.request.get('value').strip()

            config.config[title] = value

            config.put()
            memcache.delete(title, namespace='config')
            self.redirect('.')

        except Exception, err:
            vals['item'] = self.request.POST
            vals['err'] = err
            self.template( 'config-form.html', vals, 'admin' );


# Empty Form (ie. never seen ... does something then goes back to the PropertyList)
class UnCache(webbase.WebBase):
    def get(self):
        title = self.request.get('title')
        if title:
            memcache.delete(title, namespace='config')
        self.redirect('.')

# Delete
class Del(webbase.WebBase):
    def get(self):
        try:
            title = self.request.get('title').strip()
            if title:
                config = util.get_config()
                vals = {
                    'item' : {
                        'title' : title,
                        'value' : config.config[title],
                        }
                    }
                self.template( 'config-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        try:
            title = self.request.get('title').strip()
            if title:
                config = util.get_config()
                del config.config[title]
                config.put()
                memcache.delete(title, namespace='config')
            # else, just redirect to this dir
            self.redirect('.')
        except:
            self.redirect('.')

## ----------------------------------------------------------------------------
