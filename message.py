## ----------------------------------------------------------------------------
# import standard modules
# none

# Google specific modules
# none

# local modules
from models import Message
import webbase

## ----------------------------------------------------------------------------

# List
class List(webbase.WebBase):
    def get(self):
        messages = Message.all().order('-inserted')
        vals = {
            'messages' : messages,
        }
        self.template( 'message-list.html', vals, 'admin' );


# Delete
class Del(webbase.WebBase):
    def get(self):
        try:
            if self.request.get('key'):
                item = Message.get( self.request.get('key') )

                vals = {
                    'item' : item,
                    }
                self.template( 'message-del.html', vals, 'admin' );
            else:
                self.redirect('.')
        except:
            self.redirect('.')

    def post(self):
        try:
            item = Message.get( self.request.get('key') ) if self.request.get('key') else None
            if item is not None:
                try:
                    item.delete()
                    self.redirect('.')
                except:
                    vals = {
                        'item' : item,
                        'err' : 'There was an error when deleting this message, please try again'
                        }
                    self.template( 'message-del.html', vals, 'admin' );
        except:
            self.redirect('.')

## ----------------------------------------------------------------------------
