#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" WSGI application that serves blobs.
"""

import urllib

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp.util import run_wsgi_app

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    """
    """
    
    def get(self, resource, filename=''):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)
        
    
    


mapping = [
    ('/blob/([^/]+)/([^/]+)\/?', ServeHandler),
    ('/blob/([^/]+)\/?', ServeHandler),
]

def main():
    """
    """
    
    application = webapp.WSGIApplication(mapping, debug=True)
    run_wsgi_app(application)
    

