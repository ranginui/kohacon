## ----------------------------------------------------------------------------
# import standard modules
import os
#import cgi
#import logging

# Google specific
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import util
import webbase

## ----------------------------------------------------------------------------

sample_text = """\
!1 Hello, World!

This is more
paras.

 Some <pre> here.

< Some
<em>html</em>
here.

" Quote here.

!2 Inline Stuff

Some \\b{bold}.

Some \\i{italics}.

Some \\u{underline}.

Some \\b{bold}, \\i{italics}, \\u{underline} and \\c{code}.

Some \\l{links|http://news.bbc.co.uk/}.

Some \\w{wiki}, \\h{http://www.google.com/} and \\l{more links|http://news.bbc.co.uk/}.

An \\img{image|http://farm4.static.flickr.com/3102/3149653279_fbc303eb67_m.jpg},\\br{}\copy{}chilts.org.

Harder ones like \\b{bold \\i{and italic}}. Or how about \\b{bold, \\i{italic} and \\u{underline}}. And \\b{\\i{\u{all three}}}.

And a \\l{link with \\b{bold}|http://lxer.com/} here.

(Ends)
"""

sample_list = """\
!2 List Stuff

* a simple list
* here

-

* an indented list
** here

-

* an indented list
** here
* finishes on one

-

# one - simple
# two - list
# three - end

-

# this
** more
** here
# end

-

* one
## two
*** three

"""

items = [ 'rst', 'phliky', 'phliky-list', 'text', 'code' ]

class Home(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<ul>')
        for li in items:
            self.response.out.write('<li><a href="' + util.esc(li) + '.html">' + util.esc(li) + '</a></li>')
        self.response.out.write('</ul>')

class Rst(webapp.RequestHandler):
    def get(self):
        html = util.render('Hello *World*!', 'rst')
        self.response.out.write(html)

class Phliky(webapp.RequestHandler):
    def get(self):
        html = util.render(sample_text, 'phliky')
        self.response.out.write(html)

class PhlikyList(webapp.RequestHandler):
    def get(self):
        html = util.render(sample_list, 'phliky')
        self.response.out.write(html)

class Text(webapp.RequestHandler):
    def get(self):
        html = util.render(sample_text, 'text')
        self.response.out.write(html)

class Code(webapp.RequestHandler):
    def get(self):
        html = util.render(sample_text, 'code')
        self.response.out.write(html)

class Env(webbase.WebBase):
    def get(self):
        self.write( '<pre>' )
        for k, v in os.environ.items():
            self.write( self.esc("%s=%s" % (k, v)) )
        self.write( '</pre>' )

class CSV(webbase.WebBase):
    def get(self):
        self.write('<pre>')
        for row in ['one,two,three', 'another, line, right here']:
            list = row.split(',')
            self.write( repr(list) )
        self.write('</pre>')

class ThemeDir(webbase.WebBase):
    def get(self):
        dir = 'admin'
        self.response.headers['Content-Type'] = 'text/plain'
        self.write('Files:')
        dir = os.path.join(os.path.dirname(__file__), 'theme', 'admin')
        for dirname, dirnames, filenames in os.walk( dir ):
            for subdirname in dirnames:
                self.write(os.path.join(dirname, subdirname))
            for filename in filenames:
                self.write(os.path.join(dirname, filename))

## ----------------------------------------------------------------------------

application = webapp.WSGIApplication(
    [
        ('/test/', Home),
        ('/test/rst.html', Rst),
        ('/test/phliky.html', Phliky),
        ('/test/phliky-list.html', PhlikyList),
        ('/test/text.html', Text),
        ('/test/code.html', Code),
        ('/test/env.html', Env),
        ('/test/csv.html', CSV),
        ('/test/themedir.html', ThemeDir),
    ],
    debug = True
)

## ----------------------------------------------------------------------------

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

## ----------------------------------------------------------------------------
