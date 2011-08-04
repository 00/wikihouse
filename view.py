#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ``RequestHandler``s.
"""

import cgi

from google.appengine.ext import blobstore, db

from weblayer import RequestHandler

class BlobStoreUploadHandler(RequestHandler):
    """ Base class for handlers that accept multiple named file uploads.
    """
    
    def __init__(self, *args, **kwargs):
        super(BlobStoreUploadHandler, self).__init__(*args, **kwargs)
        self._uploads = None
        
    
    def get_uploads(self):
        if self._uploads is None:
            self._uploads = {}
            for key, value in self.request.params.items():
                if isinstance(value, cgi.FieldStorage):
                    if 'blob-key' in value.type_options:
                        value = blobstore.parse_blob_info(value)
                        self._uploads[key] = value
        return self._uploads
        
    
    


class Index(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('index.tmpl')
        
    
    


class Standard(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('standard.tmpl')
        
    
    


class Download(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('download.tmpl')
        
    
    


class Support(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('support.tmpl')
        
    
    


class Contact(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('contact.tmpl')
        
    
    


class Library(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('library.tmpl')
        
    
    



class NotFound(RequestHandler):
    """
    """
    
    def get(self, world):
        return self.render('errors/404.tmpl')
        
    
    


