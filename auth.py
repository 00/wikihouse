#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides `@auth.required` and `@auth.admin` decorators, using
  `google.appengine.api.users`.
"""

from google.appengine.api import users

def required(handler_method):
    """ Decorator to require that a user be logged in to access a handler.
    """
    
    def check_login(self, *args, **kwargs):
        user = users.get_current_user()
        if user is None:
            return self.redirect(users.create_login_url(self.request.path))
        return handler_method(self, *args, **kwargs)
        
    
    return check_login
    

def admin(handler_method):
    """ Decorator to require that a user be logged in and an admin.
    """
    
    def check_admin(self, *args, **kwargs):
        user = users.get_current_user()
        if user is None:
            return self.redirect(users.create_login_url(self.request.path))
        elif not users.is_current_user_admin():
            return self.error(403)
        return handler_method(self, *args, **kwargs)
        
    
    
    return check_admin
    

