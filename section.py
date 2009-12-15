## ----------------------------------------------------------------------------
# import standard modules
import logging

# Google specific modules
from google.appengine.ext import db
from google.appengine.api.labs.taskqueue import Task

# local modules
import models
import webbase
import formbase
import util

## ----------------------------------------------------------------------------

# list
class List(webbase.WebBase):
    def get(self):
        sections = models.Section.all()
        vals = {
            'title' : 'Section List',
            'sections' : sections
        }
        self.template( 'section-list.html', vals, 'admin' );

# form
class FormHandler(webbase.WebBase):
    def get(self):
        item = None
        if self.request.get('key'):
            item = db.get( self.request.get('key') )

        vals = {
            'item' : item,
            'types' : models.type_choices,
            'layouts' : models.layout_choices,
            }
        # blah.html = section-form.html ... but see:
        # http://groups.google.com/group/google-appengine-python/browse_thread/thread/5541f51962034e28
        self.template( 'section-form.html', vals, 'admin' );

    def post(self):
        item = None
        vals = {}
        try:
            # get all the incoming values
            path = self.request.get('path').strip()
            title = self.request.get('title').strip()
            description = self.request.get('description')
            type = self.request.get('type')
            layout = self.request.get('layout')
            logging.info('layout=' + layout)
            attribute_raw = self.request.get('attribute_raw').strip()

            # some pre-processing of the input params
            description_html = util.render(description, type)

            if self.request.get('key'):
                item = db.get( self.request.get('key') )
                item.path = path
                item.title = title
                item.description = description
                item.description_html = description_html
                item.type = type
                item.layout = layout
                item.attribute_raw = attribute_raw
            else:
                item = models.Section(
                    path = path,
                    title = title,
                    description = description,
                    description_html = description_html,
                    type = type,
                    layout = layout,
                    attribute_raw = attribute_raw,
                    )

            # update and save this section
            item.set_derivatives()
            item.put()
            # once saved, add the section to the two task queues
            item.regenerate()
            self.redirect('.')
        except Exception, err:
            vals['item'] = self.request.POST
            vals['err'] = err
            vals['types'] = models.type_choices
            vals['layouts'] = models.layout_choices
            self.template( 'section-form.html', vals, 'admin' );

## ----------------------------------------------------------------------------
