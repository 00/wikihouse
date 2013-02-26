#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Application settings.
"""

import os
from os.path import dirname, join as join_path
from secret import email, cookie as cookie_secret
try:
    from weblayer.utils import json_decode
except ImportError:
    from json import loads as json_decode

def get_data(filename, directory=None):
    if directory is None:
        directory = dirname(__file__)
    file_path = join_path(directory, filename)
    try:
        sock = open(file_path)
    except IOError:
        data = None
    else:
        data = json_decode(sock.read())
        sock.close()
    return data
    


settings = {
    'dev': os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'),
    'check_xsrf': True,
    'cookie_secret': cookie_secret,
    'moderator_email_address': email,
    'assetgen_manifest': get_data('assets.json'),
    'static_files_path': 'static',
    'static_url_prefix': u'/static/',
    'template_directories': ['templates'],
    'locale_directory': os.path.join('static', 'i18n'),
    'js_message_strings': get_data(
        'message_strings.json', 
        os.path.join('static', 'i18n')
    ),
    'default_language': 'en',
    'supported_languages': [
        # English.
        'en', 
        # French.
        'fr', 
        # Spanish.
        'es', 
        # Mandarin.
        'zh', 
        # Russian.
        'ru', 
        # Korean.
        'ko'
    ]
}
