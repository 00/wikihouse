#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides ``ManifestedStaticURLGenerator``, an implementation of
  :py:class:`~weblayer.interfaces.IStaticURLGenerator` that uses an `Assetgen`_
  manifest file to generate static urls for use in templates.
  
  _`Assetgen`: http://pypi.python.org/pypi/assetgen
  
"""

__all__ = [
    'ManifestedStaticURLGenerator'
]

from itertools import cycle

from zope.component import adapts
from zope.interface import implements

from weblayer.interfaces import IRequest, ISettings, IStaticURLGenerator
from weblayer.settings import require_setting

require_setting('static_url_prefix', default=u'/static/')
require_setting('assetgen_manifest')

class ManifestedStaticURLGenerator(object):
    """ Adapter to generate static URLs using an `Assetgen`_ manifest file.
      
      _`Assetgen`: http://pypi.python.org/pypi/assetgen
      
    """
    
    adapts(IRequest, ISettings)
    implements(IStaticURLGenerator)
    
    def __init__(self, request, settings):
        self._dev = settings.get('dev', False)
        self._host = settings.get('static_host', request.host)
        self._static_url_prefix = settings['static_url_prefix']
        self._manifest = settings['assetgen_manifest']
        self._subdomains = cycle(
            settings.get('static_subdomains', '12345')
        )
        
    
    
    def get_url(self, path):
        """ Get a fully expanded url for the given static resource ``path``.
          
          If we're in production then appends a subdomain to the beginning
          of the host, to avoid too many connections to the same url.
        """
        
        file_path = self._manifest.get(path, path)
        
        if self._dev:
            host = self._host
        else:
            host = '%s.%s' % (self._subdomains.next(), self._host)
        
        return u'//%s%s%s' % (host, self._static_url_prefix, file_path)
        
    
    

