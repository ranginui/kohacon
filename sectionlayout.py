## ----------------------------------------------------------------------------
# import standard modules

# Google specific modules
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

# local modules
from models import SectionLayout
import webbase

## ----------------------------------------------------------------------------

# Forms
class SectionLayoutForm(djangoforms.ModelForm):
    class Meta:
        model = SectionLayout
        exclude = ['owner', 'editor']

class SectionLayoutList(webbase.WebBase):
    def get(self):
        section_layouts = SectionLayout.all()
        vals = {
            'title' : 'Section Layout List',
            'section_layouts' : section_layouts
        }
        self.template( 'admin-section-layout-index.html', vals, 'admin' );

class SectionLayoutNew(webbase.WebBase):
    TYPE = 'Section Layout'
    def get(self):
        vals = {
            'type' : self.TYPE,
            'form' : SectionLayoutForm(),
            }
        self.template( 'admin-edit.html', vals, 'admin' );

    def post(self):
        form = SectionLayoutForm( self.request.POST )
        if form.is_valid():
            item = form.save( commit = False )
            item.put()
            self.redirect('.')
        else:
            vals = {
                'type' : self.TYPE,
                'form' : form
                }
            self.template( 'admin-edit.html', vals, 'admin' );

class SectionLayoutEdit(webbase.WebBase):
    TYPE = 'Section Layout'
    def get(self):
        item = db.get( self.request.get('key') )
        vals = {
            'type' : self.TYPE,
            'form' : SectionLayoutForm(instance=item),
            'item' : item
            }
        self.template( 'admin-edit.html', vals, 'admin' )

    def post(self):
        item = db.get( self.request.get('key') )
        form = SectionLayoutForm(data=self.request.POST, instance=item)
        if form.is_valid():
            item = form.save( commit = False )
            item.put()
            self.redirect('.')
        else:
            vals = {
                'type' : self.TYPE,
                'form' : form,
                'item' : item
                }
            self.template( 'admin-edit.html', vals, 'admin' );

## ----------------------------------------------------------------------------
