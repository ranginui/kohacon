## ----------------------------------------------------------------------------
# import standard modules
import logging

# Google specific modules
from google.appengine.ext import db

# local modules
import models
import webbase

## ----------------------------------------------------------------------------

# do all migrations in short steps (< 30 secs)

# Forms
class Migrate(webbase.WebBase):
    def get(self):
        logging.info('Right here')
        vals = {
            'migrations' : [
                { 'from' : 0, 'to' : 1 },
                { 'from' : 1, 'to' : 2 },
                ]
            }

        logging.info(self.request.get('from'))
        logging.info(self.request.get('to'))

        if self.request.get('from') == '0' and self.request.get('to') == '1':
            self.migrate_0_1()
        else:
            logging.info('Not doing any migration')

        self.template( 'migrate.html', vals, 'admin' );

    def migrate_0_1(self):
        logging.info('Migration 1 -> 2')
        # convert all sections to the new values
        q = db.GqlQuery("SELECT * FROM Section")
        results = q.fetch(20)
        for result in results:
            logging.info('key = ' + str(result.key()))
            delattr(result, 'layout')
            layout.section = 'new'
            result.put()

## ----------------------------------------------------------------------------
