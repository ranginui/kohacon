## ----------------------------------------------------------------------------
# import standard modules
import cgi
import os
import logging
import re

# Google specific modules
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# local modules
import webbase
from models import Section
from models import Node
import config

## ----------------------------------------------------------------------------

class LollySite(webbase.WebBase):
    def get(self):
        logging.info('Doing path ' + self.request.path)
        logging.info("Theme=" + config.value('Theme'))

        # matches:
        # - (/)
        # - (/)(intro).(html)
        # - (/blog/)(this).(html)
        # - (/something/here/)
        # - (/something/here/)(hello).(html)
        # - (/software/cil/)(hello).(cil_v1.3.2.tar.gz).(html)
        parts = re.compile('^(.*/)(([\w\._-]*)\.(\w+))?$')
        m = parts.match(self.request.path)

        this_path = m.group(1)
        this_page = m.group(3)
        this_ext = m.group(4)

        if this_page is None:
            this_page = 'index'
            this_ext = 'html'

        logging.info('path=' + this_path)
        logging.info('page=' + this_page)
        logging.info('ext=' + this_ext)

        # get _this_ section
        section_query = Section.all().filter('path =', this_path)
        section = None
        if section_query.count() > 0:
            section = section_query.fetch(1)[0]

        logging.info('section.title=' + section.title)
        logging.info('section.layout=' + section.layout.title)

        # get this stuff from the datastore
        #content_query = Node.all().filter('name =', this_page).filter('section =', section.key)
        content_query = Node.all().filter('name =', this_page)
        #content_query = Node.all().filter('section =', section.key)
        content = None
        if content_query.count() > 0:
            content = content_query.fetch(1)[0]

        # if either the section or the content is None, then return not found
        if section is None or content is None:
            self.error(404)
            return

        logging.info('content.name=' + content.name)
        logging.info('content.title=' + content.title)

        vals = {
            #'title'   : content.title,
            #'content' : content.content,
            'content' : content,
            }

        self.template( 'content.html', vals, config.value('Theme') );

## ----------------------------------------------------------------------------

application = webapp.WSGIApplication(
    [
        ('/.*', LollySite)
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
