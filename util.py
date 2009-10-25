## ----------------------------------------------------------------------------
# AppEngine independent utils to help with any app

## ----------------------------------------------------------------------------
# import standard modules
import logging
import sys
import cgi

## ----------------------------------------------------------------------------
# local modules
# from docutils.parsers import rst
# sys.path.append('/usr/share/pyshared/')
from docutils.core import publish_string

# /usr/share/pyshared/
# if os.path.isdir('pythonutils'):

import phliky

## ----------------------------------------------------------------------------
# render the content as HTML

class InvalidTypeError(Exception):
    def __init__(self, type):
        self.type = type
    def __str__(self):
        return repr(type)

def esc(text):
    return cgi.escape(text, True)

def render(text, type):
    logging.info('Doing ' + type);
    if type == 'html':
        return text

    # From: http://www.tele3.cz/jbar/rest/about.html
    #elif type == 'rst':
    #    return publish_string(
    #        source=text,
    #        settings_overrides={'file_insertion_enabled': 0, 'raw_enabled': 0},
    #        writer_name='html'
    #        )

    elif type == 'text':
        html = ''
        paras = text.split('\n\n')
        for para in paras:
            html = html + '<p>' + esc(para) + '</p>\n'
        return html

    elif type == 'code':
        return '<pre>' + esc(text) + '</pre>\n'

    elif type == 'phliky':
        return phliky.text2html(text)

    else:
        raise InvalidTypeError(type)

## ----------------------------------------------------------------------------
