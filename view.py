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
        
    
    


