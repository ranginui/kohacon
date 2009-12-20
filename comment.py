## ----------------------------------------------------------------------------
# import standard modules
import re

# Google specific modules
from google.appengine.ext.webapp import template
from google.appengine.ext import db

# local modules
import webbase
import formbase
from models import Comment

## ----------------------------------------------------------------------------

status_map = {
    'approve' : 'approved',
    'reject' : 'rejected',
}

## ----------------------------------------------------------------------------

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
            comments = Comment.all().filter('status =', 'new').order('inserted')
            vals = {
                'comments' : comments,
                }
            self.template( 'comment-index.html', vals, 'admin' )
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

                vals = {
                    'item' : item,
                    }
                self.template( 'comment-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        try:
            item = Comment.get( self.request.get('key') ) if self.request.get('key') else None
            if item is not None:
                try:
                    item.delete()
                    self.redirect('.')
                except:
                    vals = {
                        'item' : item,
                        'err' : 'There was an error when deleting this comment, please try again'
                        }
                    self.template( 'comment-del.html', vals, 'admin' );
        except:
            self.redirect('.')

## ----------------------------------------------------------------------------
