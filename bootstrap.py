#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Bootstrap the application.
"""

import logging

from weblayer import RequestHandler

import model

series = [{
        'value': 'houses',
        'label': u'Houses'
    }, {
        'value': 'a',
        'label': u'A Series'
    }, {
        'value': 'b',
        'label': u'B Series'
    }, {
        'value': 'c',
        'label': u'C Series'
    }, {
        'value': 'ac',
        'label': u'AC Series'
    }, {
        'value': 'bb',
        'label': u'BB Series'
    }, {
        'value': 'bc',
        'label': u'BC Series'
    }, {
        'value': 'cc',
        'label': u'CC Series'
    }, {
        'value': 'cac',
        'label': u'CAC Series'
    }, {
        'value': 'cbc',
        'label': u'CBC Series'
    }, {
        'value': 'other',
        'label': u'Other'
    }
]

class Bootstrap(RequestHandler):
    """ Setup `model.Series` instances.
    """
    
    def get(self):
        to_add = []
        i = 0
        for item in series:
            existing = model.Series.all().filter("value =", item['value']).get()
            if existing is None:
                key_name = item.pop('value')
                instance = model.Series(key_name=key_name, order=i, **item)
                to_add.append(instance)
            i = i + 1
        model.db.put(to_add)
        return 'Created %s Series instances.' % len(to_add)
        
    
    
    

