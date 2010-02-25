## ----------------------------------------------------------------------------
# Lollysite is a website builder and blogging platform for Google App Engine.
#
# Copyright (c) 2009, 2010 Andrew Chilton <andy@chilts.org>.
#
# Homepage  : http://www.chilts.org/project/lollysite/
# Ohloh     : https://www.ohloh.net/p/lollysite/
# FreshMeat : http://freshmeat.net/projects/lollysite
# Source    : http://gitorious.org/lollysite/
#
# This file is part of Lollysite.
#
# Lollysite is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Lollysite is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Lollysite.  If not, see <http://www.gnu.org/licenses/>.
#
## ----------------------------------------------------------------------------

# import standard modules
import cgi
import os
import logging
import re

# Google specific modules
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.db import GqlQuery
from google.appengine.api import mail

# local modules
import webbase
from models import Section, Node, Comment
import config

## ----------------------------------------------------------------------------

# try http://localhost:8080/_ah/queue/section-regenerate?key=agpjaGlsdHMtb3Jncg0LEgdTZWN0aW9uGGQM
class SectionRegenerate(webbase.WebBase):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.write('Started section regeneration task:')

        key = self.request.get('key')
        self.write('- key = ' + key)

        # ok, so get the section first
        section = Section.get( self.request.get('key') )
        if section is None:
            self.write('No section found')
            logging.warn( 'No section found for key: ' +  key )
            return

        # keep a count of all these things
        labels = {}
        archives = {}

        # get all the nodes
        # FixMe: why doesn't "nodes = section.nodes()" work ???
        nodes = Node.all().filter('section =', section.key())
        self.write('Nodes:')
        for node in nodes:
            self.write('- node=' + node.kind()) # FixMe: why doesn't "node.name()" work :(
            # count all of the labels
            for label in node.label:
                self.write('  - ' + label)
                if label in labels:
                    labels[label] += 1
                else:
                    labels[label] = 1

            # the archive counts
            for archive in node.archive:
                self.write('  - ' + archive)
                if archive in archives:
                    archives[archive] += 1
                else:
                    archives[archive] = 1

        # after all that, make them into a list (for ease of use in Django Templates)
        archives = [
            { 'archive' : x, 'count' : archives[x] }
            for x in sorted(archives)
            if re.search(r'^\d\d\d\d(-\d\d)?$', x, re.DOTALL | re.VERBOSE) # just get years and months
            ]
        labels = [
            { 'label' : x, 'count' : labels[x] }
            for x in sorted(labels)
            ]

        # now that we have our counts, save it as JSON
        section.archive_json = archives
        section.label_json = labels
        section.put()

        self.write('Finished')

# try http://localhost:8080/_ah/queue/section-check-duplicate-nodes?key=?&name=?
class SectionCheckDuplicateNodes(webbase.WebBase):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.write('Started section duplicate node check:')

        section_key = self.request.get('section_key')
        name = self.request.get('name')
        self.write('- key  = ' + section_key)
        self.write('- name = ' + name)

        # get the section first (and if the section_key is crap just finish)
        section = None
        try:
            section = Section.get( self.request.get('section_key') )
        except:
            # by just returning here, it ends up a 200, so all is good
            return

        if section is None:
            self.write('No section found')
            logging.warn( 'No section found for key: ' +  section_key )
            return

        nodes = Node.all().filter('section =', section).filter('name =', name)
        if nodes.count() <= 1:
            msg = 'Only [%d] nodes of this name in this section' % nodes.count()
            self.write(msg)
            return

        msg = 'More than one node named [%s] in section [%s]' % (name, section.path)
        self.write(msg)
        logging.warn(msg)
        admin_email = util.config_value('Admin Email')
        if not mail.is_email_valid(admin_email):
            return

        url_edit = util.construct_url() + '/admin/node/'
        body = 'Section %s has two nodes named %s ' % (section.path, name)
        mail.send_mail(admin_email, admin_email, 'Duplicate node name in section ' + section.path, body)

# try http://localhost:8080/_ah/queue/node-regenerate?key=?
class NodeRegenerate(webbase.WebBase):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.write('Started node regeneration task:')

        key = self.request.get('key')
        self.write('- key = ' + key)

        # ok, so get the section first
        node = db.Model.get( self.request.get('key') )
        if node is None:
            self.write('No node found')
            return

        self.write('Section = ' + node.section.path)
        self.write('Node = ' + node.name)

        # get the approved comments and update the node itself
        comments = Comment.all().filter('node =', node.key()).filter('status =', 'approved')
        node.comment_count = comments.count()
        self.write('- count=' + str(node.comment_count))
        node.put()
        self.write('Finished')

application = webapp.WSGIApplication(
    [
        # these locations are the default
        # See: http://code.google.com/appengine/docs/python/taskqueue/overview.html#Queue_Default_URLs
        ('/_ah/queue/section-regenerate', SectionRegenerate),
        ('/_ah/queue/node-regenerate', NodeRegenerate),
        ('/_ah/queue/section-check-duplicate-nodes', SectionCheckDuplicateNodes),
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
