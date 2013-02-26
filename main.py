#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides `main()` application entrypoint.
"""

import patch
patch.sys_path()

from google.appengine.ext.webapp.util import run_wsgi_app
from weblayer import Bootstrapper, WSGIApplication

from asset import ManifestedStaticURLGenerator
from config import settings
from template import Renderer
from urls import mapping

bootstrapper = Bootstrapper(settings=settings, url_mapping=mapping)
app = WSGIApplication(
    *bootstrapper(
        StaticURLGenerator=ManifestedStaticURLGenerator,
        TemplateRenderer=Renderer
    )
)
