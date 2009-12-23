## ----------------------------------------------------------------------------
# AppEngine independent utils to help with any app

## ----------------------------------------------------------------------------
# import standard modules
import logging
import sys
import cgi
import re
import datetime
import re

## ----------------------------------------------------------------------------
# local modules

import textile
import markdown

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
    if type is None or type.strip() == '':
        return ''

    text = re.sub('\r', '', text);
    logging.info('Doing ' + type);
    if type == 'html':
        return text

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

    elif type == 'textile':
        return textile.textile(text)

    elif type == 'markdown':
        return markdown.markdown(text)

    else:
        raise InvalidTypeError(type)

def urlify(title):
    name = title.lower()

    # special case to remove ' completely (for things like: let's it's and o'clock)
    name = re.sub(r'\'', '', name )

    # replace anything not a letter or number with a dash
    name = re.sub(r'[^a-z0-9]+', '-', name )

    # replace any dashes at start or end with one
    name = re.sub(r'-+', '-', name )
    name = re.sub(r'^-', '', name )

    # and multiple dashes with just one
    name = re.sub(r'-$', '', name )

    return name

def str_to_datetime(str):
    """ takes strings of the form yyyy-mm-dd hh:mm:ss and returns a datetime """
    a = [ int(x) for x in re.split(r'[ \-:]', str) ]
    dt = datetime.datetime(a[0], a[1], a[2], a[3], a[4], a[5])
    return dt

## ----------------------------------------------------------------------------
