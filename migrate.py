## ----------------------------------------------------------------------------
# import standard modules
import logging

# Google specific modules
from google.appengine.ext import db

# local modules
import webbase

## ----------------------------------------------------------------------------
# define all the entity types we have

class Section(db.Expando):
    pass

class Node(db.Expando):
    pass

# migration list
migrations = [
    '20091122a_RemoveUnusedArchive',
    '20091123a_GenerateLabelRaw',
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

## ----------------------------------------------------------------------------
