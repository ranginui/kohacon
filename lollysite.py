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
        if section_query.count() == 0:
            self.error(404)
            return

        section = section_query.fetch(1)[0]

        # get this stuff from the datastore

        # if either the section or the content is None, then return not found
        #if section is None or node is None:
        #    self.error(404)
        #    return

        # if this is an index, call a different template
        if this_page == 'index':
            #nodes_query = Node.all().filter('section =', section.key()).order('-inserted')
            #nodes = nodes_query.fetch(10)

            nodes = self.latest_nodes(section, 10)
            vals = {
                'section' : section,
                'nodes'   : nodes,
                }
            self.template( 'index.html', vals, config.value('Theme') );

        elif this_page == 'rss20' and this_ext == 'xml':
            nodes = self.latest_nodes(section, 10)
            vals = {
                'section' : section,
                'nodes'   : nodes,
                }
            self.template( 'rss20.xml', vals, 'rss' );

        elif this_page == 'sitemapindex' and this_ext == 'xml':
            sections = Section.all()
            vals = {
                'sections' : sections,
                }
            self.template( 'sitemapindex.xml', vals, 'sitemaps' );

        elif this_page == 'urlset' and this_ext == 'xml':
            vals = {
                'section' : section,
                'nodes'   : Node.all().filter('section =', section.key())
                }
            self.template( 'urlset.xml', vals, 'sitemaps' );

        else:
            node_query = Node.all().filter('section =', section.key()).filter('name =', this_page)
            if node_query.count() == 0:
                self.error(404)
                return
            node = node_query.fetch(1)[0]
            logging.info('node.name=' + node.name)
            logging.info('node.title=' + node.title)
            vals = {
                'section' : section,
                'node'    : node,
                }
            self.template( 'page.html', vals, config.value('Theme') );

    def latest_nodes(self, section, limit):
        logging.info('Getting latest nodes for ' + section.path)
        nodes_query = Node.all().filter('section =', section.key()).order('-inserted')
        nodes = nodes_query.fetch(limit)
        return nodes

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
