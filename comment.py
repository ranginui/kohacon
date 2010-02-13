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
from google.appengine.ext.webapp import template
from google.appengine.ext import db

# local modules
from models import Comment, Section
import models
import webbase
import error

## ----------------------------------------------------------------------------

status_map = {
    'approve' : 'approved',
    'reject' : 'rejected',
}

## ----------------------------------------------------------------------------

page_count = 20

# Forms
class Index(webbase.WebBase):
    def get(self):
        # see if there is a key
        comment = None
        status = None
        try:
            comment = Comment.get( self.request.get('key') )
            status = self.request.get('status')
        except db.BadKeyError:
            pass

        if comment is None:
            # show all the 'new' comments
            comments = Comment.all().filter('status =', 'new').order('inserted').fetch(page_count+1)
            more = True if len(comments) > page_count else False
            comments = comments[:page_count]
            vals = {
                'comments' : comments,
                'more'     : more,
                }
            self.template( 'comment-list.html', vals, 'admin' )
        else:
            comment.status = status_map[status]
            comment.put()
            comment.node.regenerate()
            self.redirect('./')
            return

# Edit
class Edit(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = Comment.get( self.request.get('key') )
        else:
            raise error.RequiresEntityError("Needs a comment key (ie. can't add new comments in the admin interface)")

        vals = {
            'item' : item,
            'sections' : Section.all(),
            'types' : models.type_choices
            }
        self.template( 'comment-form.html', vals, 'admin' );

    def post(self):
        item = None
        vals = {}
        try:
            # get all the incoming values
            name = self.request.get('name')
            email = self.request.get('email')
            website = self.request.get('website')
            comment = self.request.get('comment')

            if self.request.get('key'):
                item = Comment.get( self.request.get('key') )
                item.name = name
                item.email = email
                item.website = website
                item.comment = comment
            else:
                # we have no ability to add comments, so fail here
                raise error.RequiresEntityError("Needs a comment key (ie. can't add new comments in the admin interface)")

            # update and save this comment
            item.set_derivatives()
            item.put()

            # don't need to item.node.regenerate() since the status is _not_ changing

            self.redirect('.')
        except Exception, err:
            vals['item'] = self.request.POST
            vals['err'] = err
            vals['sections'] = Section.all()
            vals['types'] = models.type_choices
            self.template( 'comment-form.html', vals, 'admin' );


# Delete
class Del(webbase.WebBase):
    def get(self):
        try:
            if self.request.get('key'):
                item = Comment.get( self.request.get('key') )
                if item is None:
                    self.redirect('.')
                    return

                vals = {
                    'item' : item,
                    }
                self.template( 'comment-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        item = None
        try:
            item = Comment.get( self.request.get('key') ) if self.request.get('key') else None
            if item is None:
                self.redirect('.')
                return

            item.delete()
            self.redirect('.')
        except:
            vals = {
                'item' : item,
                'err' : 'There was an error when deleting this comment, please try again'
                }
            self.template( 'comment-del.html', vals, 'admin' );

class DelAll(webbase.WebBase):
    def post(self):
        try:
            items = Comment.get( self.request.get_all('keys') )
            for item in items:
                item.delete()

        except:
            pass # just going to redirect to '.' anyway

        self.redirect('.')


## ----------------------------------------------------------------------------
