## ----------------------------------------------------------------------------
# import standard modules
import re
import logging

# Google specific modules
from google.appengine.ext.webapp import template
from google.appengine.ext import db

# local modules
import webbase
from models import Comment

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
