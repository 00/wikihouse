#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Database ``Model`` classes.
"""

from google.appengine.ext import blobstore, db

class Series(db.Model):
    """ A WikiHouse standard design series.
    """
    
    v = db.IntegerProperty(default=1)                   # version
    c = db.DateTimeProperty(auto_now_add=True)          # created
    m = db.DateTimeProperty(auto_now=True)              # modified
    
    order = db.IntegerProperty()
    title = db.StringProperty()
    description = db.TextProperty(default='')
    
    @classmethod
    def get_all(cls):
        return cls.all().order('order')
        
    
    
    @property
    def designs(self):
        query = Design.all().filter("status =", u'approved')
        return query.filter("series =", self.key())
        
    
    


class Design(db.Model):
    """ A design in the WikiHouse library.
    """
    
    v = db.IntegerProperty(default=1)                   # version
    c = db.DateTimeProperty(auto_now_add=True)          # created
    m = db.DateTimeProperty(auto_now=True)              # modified
    
    
    component = db.BooleanProperty(required=True, default=False)
    title = db.StringProperty(required=True)
    description = db.TextProperty(required=True)
    series = db.ListProperty(db.Key)
    
    user = db.UserProperty(auto_current_user_add=True)
    country = db.StringProperty()                       # X-AppEngine-Country
    
    status = db.StringProperty(
        choices=[
            u'pending', 
            u'approved', 
            u'rejected'
        ],
        default=u'pending'
    )
    verification = db.StringProperty(
        choices=[
            u'unverified', 
            u'verified', 
            u'built'
        ],
        default=u'unverified'
    )
    notes = db.TextProperty()
    sketchup_version = db.StringProperty()
    
    model = blobstore.BlobReferenceProperty()
    model_preview = blobstore.BlobReferenceProperty()
    model_preview_reverse = blobstore.BlobReferenceProperty()
    sheets = blobstore.BlobReferenceProperty()
    sheets_preview = blobstore.BlobReferenceProperty()
    

