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
import logging

# Google specific modules
from google.appengine.ext import db

# local modules
import webbase
from models import Section
from models import Node

## ----------------------------------------------------------------------------
# define all the entity types we have

# migration list
migrations = [
    '20091122a_RemoveUnusedArchive',
    '20091123a_GenerateLabelRaw',
    '20091124a_MakeSectionRightAgain',
    ]

## ----------------------------------------------------------------------------

# do all migrations in short steps (< 30 secs)

# Forms
class Migrate(webbase.WebBase):
    def get(self):
        logging.info('Right here')
        vals = {
            'migrations' : migrations
            }

        m = self.request.get('m')
        if m == '20091122a_RemoveUnusedArchive':
            self.m_20091122a_RemoveUnusedArchive()
        elif m == '20091123a_GenerateLabelRaw':
            self.m_20091123a_GenerateLabelRaw()
        elif m == '20091124a_MakeSectionRightAgain':
            self.m_20091124a_MakeSectionRightAgain()
        else:
            logging.info('Not doing any migration')

        self.template( 'migrate.html', vals, 'admin' )

    def m_20091122a_RemoveUnusedArchive(self):
        logging.info('20091122a_RemoveUnusedArchive')
        nodes = db.GqlQuery("SELECT * FROM Node")
        new = []
        for n in nodes:
            changed = False
            for attr in ['archive_day', 'archive_month', 'archive_year']:
                if hasattr(n, attr):
                    logging.info('This entity %s has %s' % (str(n.key()), attr))
                    delattr(n, attr)
                    changed = True
            if changed:
                new.append(n)
        db.put(new)
        logging.info('new.count()' + str(new.count(new)))

    def m_20091123a_GenerateLabelRaw(self):
        logging.info('20091123a_GenerateLabelRaw')
        nodes = db.GqlQuery("SELECT * FROM Node")
        new = []
        for n in nodes:
            if hasattr(n, 'label'):
                n.label_raw = ','.join(n.label)
            else:
                n.label_raw = ''
            logging.info('label_raw=' + n.label_raw)
            new.append(n)
        db.put(new)

    def m_20091124a_MakeSectionRightAgain(self):
        logging.info('20091124a_MakeSectionRightAgain')
        sections = db.GqlQuery("SELECT * FROM Section")
        new = []
        for s in sections:
            s.attribute_raw = ''
            s.attribute = s.attribute_raw.split()
            new.append(s)
        logging.info('Putting...')
        db.put(new)

## ----------------------------------------------------------------------------
