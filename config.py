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
