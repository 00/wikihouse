#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Bootstrap the application.
"""

import logging
import yaml

from weblayer import RequestHandler

import model

class Bootstrap(RequestHandler):
    """ Delete all existing `model.Series` and `model.Quote` instances and create
      new instances corresponding to `series.yaml` and `quotes.yaml`.
    """
    
    def bootstrap_series(self):
        # Delete existing (presumes there won't ever be more than 300).
        existing = model.Series.all().fetch(300)
        number_removed = len(existing)
        model.db.delete(existing)
        
        # Create new.
        sock = open('series.yaml', 'r')
        series = yaml.load(sock)
        sock.close()
        to_add = []
        i = 0
        for item in series:
            kwargs = item.copy()
            key_name = kwargs.pop('value')
            instance = model.Series(key_name=key_name, order=i, **kwargs)
            to_add.append(instance)
            i = i + 1
        number_added = len(to_add)
        model.db.put(to_add)
        
        # Return how many we created and deleted.
        return 'Deleted %s and created %s `model.Series` instances.' % (
            number_removed,
            number_added
        )
        
    
    
    def bootstrap_quotes(self):
        # Delete existing (presumes there won't ever be more than 300).
        existing = model.Quote.all().fetch(300)
        number_removed = len(existing)
        model.db.delete(existing)
        
        # Create new.
        sock = open('quotes.yaml', 'r')
        series = yaml.load(sock)
        sock.close()
        to_add = []
        for item in series:
            kwargs = item.copy()
            key_name = kwargs.pop('org')
            instance = model.Quote(key_name=key_name, **kwargs)
            to_add.append(instance)
        number_added = len(to_add)
        model.db.put(to_add)
        
        # Return how many we created and deleted.
        return 'Deleted %s and created %s `model.Quote` instances.' % (
            number_removed,
            number_added
        )
        
    
    
    def get(self):
        return '<br />%s' % (
            #self.bootstrap_series(),
            self.bootstrap_quotes()
        )
        
    
    

