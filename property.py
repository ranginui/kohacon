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
from models import Property
import webbase
import config

## ----------------------------------------------------------------------------

# List
class List(webbase.WebBase):
    def get(self):
        properties = Property.all()
        vals = {
            'title' : 'Property List',
            'properties' : properties,
            'config' : config,
        }
        self.template( 'property-list.html', vals, 'admin' );


# Edit
class Edit(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = Property.get( self.request.get('key') )

        vals = {
            'item' : item,
            }
        self.template( 'property-form.html', vals, 'admin' );

    def post(self):
        item = None
        vals = {}
        try:
            # get all the incoming values
            title = self.request.get('title').strip()
            value = self.request.get('value').strip()

            if self.request.get('key'):
                item = Property.get( self.request.get('key') )
                item.title = title
                item.value = value
            else:
                item = Property(
                    title = title,
                    value = value,
                    )

            item.put()
            memcache.delete(title, namespace='property')
            self.redirect('.')

        except Exception, err:
            vals['item'] = self.request.POST
            vals['err'] = err
            self.template( 'property-form.html', vals, 'admin' );

# Empty Form (ie. never seen ... does something then goes back to the PropertyList)
class UnCache(webbase.WebBase):
    def get(self):
        title = self.request.get('title')
        memcache.delete(title, namespace='property')
        self.redirect('.')

# Delete
class Del(webbase.WebBase):
    def get(self):
        try:
            if self.request.get('key'):
                item = Property.get( self.request.get('key') )

                vals = {
                    'item' : item,
                    }
                self.template( 'property-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        try:
            item = Property.get( self.request.get('key') ) if self.request.get('key') else None
            if item is not None:
                try:
                    item.delete()
                    memcache.delete(item.title, namespace='property')
                    self.redirect('.')
                except:
                    vals = {
                        'item' : item,
                        'err' : 'There was an error when deleting this property, please try again'
                        }
                    self.template( 'property-del.html', vals, 'admin' );
        except:
            self.redirect('.')

## ----------------------------------------------------------------------------
