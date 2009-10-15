## ----------------------------------------------------------------------------
# import standard modules

# Google Specific
from google.appengine.ext.webapp import template

# local
import config

## ----------------------------------------------------------------------------

def cfg(title):
    return config.value(title)

register = template.create_template_register()
register.filter(cfg)

## ----------------------------------------------------------------------------
