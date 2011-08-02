#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ``RequestHandler``s.
"""

from weblayer import RequestHandler


class Index(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('index.tmpl')
        
    
    


class NotFound(RequestHandler):
    """
    """
    
    def get(self, world):
        return self.render('index.tmpl')
        
    
    


