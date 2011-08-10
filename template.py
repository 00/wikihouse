#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weblayer.template import MakoTemplateRenderer

class Renderer(MakoTemplateRenderer):
    """ `Mako <http://www.makotemplates.org/>`_ template renderer that
      doesn't cache modules in a directory.
    """
    
    def __init__(self, *args, **kwargs):
        # Don't cache modules in a directory.
        kwargs['module_directory'] = None
        super(Renderer, self).__init__(*args, **kwargs)
        
    
    

