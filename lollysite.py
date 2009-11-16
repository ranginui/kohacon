## ----------------------------------------------------------------------------
# import standard modules
import cgi
import os
import logging
import re
import urllib

# Google specific modules
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# local modules
import webbase
from models import Section
from models import Node
from models import Comment
import config
import util

## ----------------------------------------------------------------------------
# regexes

# matches:
# - (/)
# - (/)(intro).(html)
# - (/blog/)(this).(html)
# - (/something/here/)
# - (/something/here/)(hello).(html)
# - (/software/cil/)(cil_v1.3.2.tar.gz).(html)
# - (/software/cil/)(label:this).(html)
parts = re.compile('^(.*/)(([\w\._:-]*)\.(\w+))?$')

label_page = re.compile('^label:(.+)$', re.DOTALL | re.VERBOSE)

## ----------------------------------------------------------------------------

class LollySite(webbase.WebBase):
    def get(self):
        path = urllib.unquote(self.request.path)
        m = parts.search(path)

        if m is None:
            self.error(404)
            return

        this_path = m.group(1)
        this_page = m.group(3) or 'index'
        this_ext = m.group(4) or 'html'

        if this_page is None:
            this_page = 'index'
            this_ext = 'html'

        section = Section.all().filter('path =', this_path).get()
        if section is None:
            logging.info('404: This section not found')
            self.error(404)
            return

        # if this is an index, call a different template
        if this_page == 'index' and this_ext == 'html':
            # index.html
            nodes = self.latest_nodes(section, 10)
            vals = {
                'section' : section,
                'nodes'   : nodes,
                }
            self.template( 'blog-index.html', vals, config.value('Theme') );

        elif this_page == 'rss20' and this_ext == 'xml':
            # rss20.xml
            nodes = self.latest_nodes(section, 10)
            vals = {
                'section' : section,
                'nodes'   : nodes,
                }
            self.response.headers['Content-Type'] = 'application/rss+xml'
            self.template( 'rss20.xml', vals, 'rss' );

        elif this_page == 'sitemapindex' and this_ext == 'xml':
            # sitemapindex.xml
            sections = Section.all()
            vals = {
                'sections' : sections,
                }
            self.response.headers['Content-Type'] = 'text/xml'
            self.template( 'sitemapindex.xml', vals, 'sitemaps' );

        elif this_page == 'urlset' and this_ext == 'xml':
            # urlset.xml
            vals = {
                'section' : section,
                'nodes'   : Node.all().filter('section =', section.key())
                }
            self.response.headers['Content-Type'] = 'text/xml'
            self.template( 'urlset.xml', vals, 'sitemaps' );

        elif label_page.search(this_page) and this_ext == 'html':
            # path =~ 'label:something.html'
            m = label_page.search(this_page)
            label = m.group(1)
            logging.info('m=' + repr(m))
            logging.info('Inside a label (%s) page' % label)
            vals = {
                'section' : section,
                'nodes'   : Node.all().filter('section =', section.key()).filter('label =', label),
                'label'   : label
                }
            self.template( 'label-index.html', vals, config.value('Theme') );

        elif this_page == 'comment' and this_ext == 'html':
            # get the comment if it exists
            try:
                comment = Comment.get( self.request.get('key') )
            except db.BadKeyError:
                self.error(404)
                return

            if comment is None:
                self.error(404)
                return

            vals = {
                'section' : section,
                'node'    : comment.node,
                'comment' : comment,
                }
            self.template( 'comment.html', vals, config.value('Theme') );

        else:
            # get the node itself
            node_query = Node.all().filter('section =', section.key()).filter('name =', this_page)
            if node_query.count() == 0:
                logging.info('404: no nodes in this section (%s) of that name (%s.%s)' % (section.path, this_page, this_ext))
                self.error(404)
                return
            node = node_query.fetch(1)[0]
            logging.info('node.name=' + node.name)
            logging.info('node.title=' + node.title)

            # get the approved comments
            comments = Comment.all().filter('node =', node.key()).filter('status =', 'approved').order('inserted')

            vals = {
                'section' : section,
                'node'    : node,
                'comments' : comments,
                }
            self.template( 'node.html', vals, config.value('Theme') );

    def post(self):
        path = urllib.unquote(self.request.path)
        m = parts.search(path)

        if m is None:
            self.error(404)
            return

        this_path = m.group(1)
        this_page = m.group(3) or 'index'
        this_ext = m.group(4) or 'html'

        logging.info('Page details:')
        logging.info('- ' + this_path)
        logging.info('- ' + this_page)
        logging.info('- ' + this_ext)

        # get section and node
        section = Section.all().filter('path =', this_path).get()
        node = Node.all().filter('section =', section).get()

        if section is None or node is None:
            self.error(404)
            return

        logging.info(section.path)
        logging.info(node.name)

        self.request.charset = 'utf8'

        logging.info(self.request.POST['node'])
        logging.info(self.request.POST['name'])
        logging.info(self.request.POST['comment'])
        logging.info(self.request.POST['email'])
        logging.info(self.request.POST['website'])

        # remove the horribleness from comment
        comment_text = re.sub('\r', '', self.request.POST['comment']);

        if this_page == 'comment' and this_ext == 'html':
            # comment submission for each section
            logging.info('saving comment')
            node = db.get( self.request.POST['node'] )
            comment = Comment(
                node = node,
                name = self.request.POST['name'],
                email = self.request.POST['email'],
                website = self.request.POST['website'],
                comment = comment_text,
                comment_html = util.render(comment_text, 'text'),
                )
            comment.put()
            # redirect to the comment page
            self.redirect('comment.html?key=' + str(comment.key()))
            return
        else:
            # not found
            self.error(404)
            return

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
