## ----------------------------------------------------------------------------
# import standard modules

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

## ----------------------------------------------------------------------------
