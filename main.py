#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides `main()` application entrypoint.
"""

import os
from os.path import dirname, join as join_path

import patch
patch.sys_path()

from google.appengine.ext.webapp.util import run_wsgi_app
from weblayer import Bootstrapper, WSGIApplication
from weblayer.utils import json_decode

from asset import ManifestedStaticURLGenerator
from secret import emails, cookie as cookie_secret
from template import Renderer
from urls import mapping

def get_data(filename, directory=None):
    if directory is None:
        directory = dirname(__file__)
    file_path = join_path(directory, filename)
    sock = open(file_path)
    data = json_decode(sock.read())
    sock.close()
    return data
    


config = {
    'dev': os.environ['SERVER_SOFTWARE'].startswith('Dev'),
    'cookie_secret': cookie_secret,
    'moderation_notification_email_addresses': emails,
    'assetgen_manifest': get_data('assets.json'),
    'static_files_path': 'static',
    'template_directories': ['templates'],
    'locale_directory': os.path.join('static', 'i18n'),
    'js_message_strings': get_data(
        'message_strings.json', 
        os.path.join('static', 'i18n')
    ),
    'default_language': 'en',
    'supported_languages': ['en', 'ko']
}

def main():
    """ Bootstrap and run the `weblayer` based WSGI application.
    """
    
    # Run the application.
    bootstrapper = Bootstrapper(settings=config, url_mapping=mapping)
    run_wsgi_app(
        WSGIApplication(
            *bootstrapper(
                StaticURLGenerator=ManifestedStaticURLGenerator,
                TemplateRenderer=Renderer
            )
        )
    )
    

