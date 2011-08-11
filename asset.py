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
        self._host_url = settings.get('static_host_url', request.host_url)
        self._static_url_prefix = settings['static_url_prefix']
        self._manifest = settings['assetgen_manifest']
        
    
    
    def get_url(self, path):
        """ Get a fully expanded url for the given static resource ``path``.
        """
        
        file_path = self._manifest.get(path, path)
        return u'%s%s%s' % (
            self._host_url, 
            self._static_url_prefix, 
            file_path
        )
        
    
    

