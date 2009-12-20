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
from google.appengine.api import mail

# local modules
import webbase
from models import Section
from models import Node
from models import Comment
from models import Message
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
archive_page = re.compile('^archive:(\d\d\d\d(-\d\d(-\d\d)?)?)$', re.DOTALL | re.VERBOSE)

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
            vals = {
                'section' : section,
                }
            self.template(  section.layout + '-index.html', vals, config.value('Theme') );

        elif this_page == 'contact' and this_ext == 'html' and section.has('contact-form'):
            logging.info('right here')
            # contact.html
            node = Node.all().filter('section =', section.key()).filter('name =', 'contact').get()
            vals = {
                'section' : section,
                'node'    : node,
                }
            self.template(  'contact.html', vals, config.value('Theme') );

        elif this_page == 'rss20' and this_ext == 'xml':
            # rss20.xml
            nodes = self.latest_nodes(section, 'index-entry', 10)
            vals = {
                'section' : section,
                'nodes'   : nodes,
                }
            self.response.headers['Content-Type'] = 'application/rss+xml'
            self.template( 'rss20.xml', vals, 'rss' );

        elif this_page == 'sitefeed' and this_ext == 'xml' and section.has('sitefeed'):
            # sitefeed.xml
            nodes = Node.all().filter('attribute =', 'index-entry').order('-inserted').fetch(10)
            vals = {
                'section' : section,
                'nodes'   : nodes,
                }
            self.response.headers['Content-Type'] = 'application/rss+xml'
            self.template( 'rss20.xml', vals, 'rss' );

        elif this_page == 'sitemapindex' and this_ext == 'xml':
            # sitemapindex.xml
            vals = {
                'sections' : Section.all().filter('attribute =', 'sitemap-entry').order('inserted'),
                }
            self.response.headers['Content-Type'] = 'text/xml'
            self.template( 'sitemapindex.xml', vals, 'sitemaps' );

        elif this_page == 'urlset' and this_ext == 'xml':
            # urlset.xml
            vals = {
                'section' : section,
                'nodes'   : Node.all().filter('section =', section.key()).filter('attribute =', 'index-entry').order('inserted')
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
                'nodes'   : Node.all().filter('section =', section.key()).filter('label =', label).order('-inserted'),
                'label'   : label
                }
            self.template( 'label-index.html', vals, config.value('Theme') );

        elif archive_page.search(this_page) and this_ext == 'html':
            # path =~ 'archive:2009.html'
            m = archive_page.search(this_page)
            archive = m.group(1)
            logging.info('archive=' + archive)
            vals = {
                'section' : section,
                'nodes'   : Node.all().filter('section =', section.key()).filter('archive =', archive).order('-inserted'),
                'archive' : archive
                }
            self.template( 'archive-index.html', vals, config.value('Theme') );

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

            # get the approved comments (but only if we know some are there, save a trip to the datastore)
            comments = None
            if node.comment_count:
                comments = Comment.all().filter('node =', node.key()).filter('status =', 'approved').order('inserted')

            vals = {
                'section'  : section,
                'node'     : node,
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

        # get section and node
        section = Section.all().filter('path =', this_path).get()
        node = Node.all().filter('section =', section).get()

        if section is None or node is None:
            self.error(404)
            return

        self.request.charset = 'utf8'

        # remove the horribleness from comment
        if this_page == 'comment' and this_ext == 'html':
            # comment submission for each section
            node = Node.get( self.request.POST['node'] )
            name = self.request.POST['name']
            email = self.request.POST['email']
            website = self.request.POST['website']
            comment_text = re.sub('\r', '', self.request.POST['comment']);

            # now create the comment
            comment = Comment(
                node = node,
                name = name,
                email = email,
                website = website,
                comment = comment_text,
                comment_html = util.render(comment_text, 'text'),
                )
            comment.put()

            # send a mail to the admin
            admin_email = config.value('Admin Email')
            if mail.is_email_valid(admin_email):
                url_mod = 'http://www.' + config.value('Naked Domain') + '/admin/comment/?key=' + str(comment.key()) + ';status='
                url_del = 'http://www.' + config.value('Naked Domain') + '/admin/comment/del.html?key='+ str(comment.key())

                body = 'Comment from ' + name + '<' + email + '>\n'
                body = body + website + '\n\n'
                body = body + comment_text + '\n\n'
                body = body + '---\n\nActions\n\n'
                body = body + 'Approve = ' + url_mod + 'approve\n'
                body = body + 'Reject  = ' + url_mod + 'reject\n'
                body = body + 'Delete  = ' + url_del + '\n'
                mail.send_mail(admin_email, admin_email, 'New comment on ' + section.path + node.name + '.html', body)
            else:
                # don't do anything
                logging.info('No valid email set, skipping sending admin an email for new comment')

            # redirect to the comment page
            self.redirect('comment.html?key=' + str(comment.key()))
            return

        elif this_page == 'contact' and this_ext == 'html':
            # comment submission for each section
            name = self.request.POST['name']
            email = self.request.POST['email']
            website = self.request.POST['website']
            subject = self.request.POST['subject']
            message = re.sub('\r', '', self.request.POST['message']);

            # now create the message
            msg = Message(
                name = name,
                email = email,
                website = website,
                subject = subject,
                message = message,
                )
            msg.put()

            # send a mail to the admin
            admin_email = config.value('Admin Email')
            if mail.is_email_valid(admin_email):
                body =        'name    : ' + name + '\n'
                body = body + 'email   : ' + email + '\n'
                body = body + 'website : ' + website + '\n'
                body = body + 'subject : ' + subject + '\n'
                body = body + message + '\n'
                mail.send_mail(admin_email, admin_email, '[Contact] ' + subject, body)
            else:
                # don't do anything
                logging.info('No valid email set, skipping sending admin an email for new contact message')

            self.redirect('.')
            return
        else:
            # not found
            self.error(404)
            return

    def latest_nodes(self, section, attribute, limit):
        logging.info('Getting latest nodes (with attribute ' +  attribute + ' for ' + section.path)
        nodes = Node.all().filter('section =', section.key()).filter('attribute =', attribute).order('-inserted').fetch(limit)
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
