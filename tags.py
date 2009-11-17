## ----------------------------------------------------------------------------
# import standard modules
import cgi

# Google Specific
from google.appengine.ext.webapp import template

# local
import config

## ----------------------------------------------------------------------------

register = template.create_template_register()

# config.value should never (usually?) raise an exception
def cfg(title):
    return config.value(title)

register.filter(cfg)

# takes an array and puts into separate lines (after making HTML safe)
def list(l):
    l = '\n'.join(l)
    return cgi.escape(l, True)

register.filter(list)

## ----------------------------------------------------------------------------
