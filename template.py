#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weblayer.template import MakoTemplateRenderer
from weblayer.template import DEFAULT_BUILT_INS

from google.appengine.api import users

built_ins = DEFAULT_BUILT_INS.copy()
built_ins['users'] = users

class Renderer(MakoTemplateRenderer):
    """ `Mako <http://www.makotemplates.org/>`_ template renderer that:
      
      * provides `google.appengine.api.users` as `users`
      * doesn't cache modules in a directory
      
    """
    
    def __init__(self, *args, **kwargs):
        # Don't cache modules in a directory.
        kwargs['module_directory'] = None
        # Provide `google.appengine.api.users`.
        kwargs['built_ins'] = built_ins
        super(Renderer, self).__init__(*args, **kwargs)
        
    
    

