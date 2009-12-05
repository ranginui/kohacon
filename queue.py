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

# local modules
import webbase
from models import Section
from models import Node

## ----------------------------------------------------------------------------

# try http://localhost:8080/_ah/queue/section-regenerate?key=agpjaGlsdHMtb3Jncg0LEgdTZWN0aW9uGGQM
class SectionRegenerate(webbase.WebBase):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.write('Started task:')

        key = self.request.get('key')
        self.write('- key = ' + key)
        logging.info( 'Regenerating ' +  key )

        # ok, so get the section first
        section = db.get( self.request.get('key') )
        if section is None:
            self.write('No section found')
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

application = webapp.WSGIApplication(
    [
        # these locations are the default
        # See: http://code.google.com/appengine/docs/python/taskqueue/overview.html#Queue_Default_URLs
        ('/_ah/queue/section-regenerate', SectionRegenerate),
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
