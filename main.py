#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides `main()` application entrypoint.
"""

import os
import patch
patch.sys_path()

from google.appengine.ext.webapp.util import run_wsgi_app
from weblayer import Bootstrapper, WSGIApplication

from asset import get_manifest, ManifestedStaticURLGenerator
from secret import emails, cookie as cookie_secret
from template import Renderer
from urls import mapping

config = {
    'dev': os.environ['SERVER_SOFTWARE'].startswith('Dev'),
    'cookie_secret': cookie_secret,
    'moderation_notification_email_addresses': emails,
    'assetgen_manifest': get_manifest(),
    'static_files_path': 'static',
    'template_directories': ['templates']
}

def main():
    bootstrapper = Bootstrapper(settings=config, url_mapping=mapping)
    run_wsgi_app(
        WSGIApplication(
            *bootstrapper(
                StaticURLGenerator=ManifestedStaticURLGenerator,
                TemplateRenderer=Renderer
            )
        )
    )
    

