#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides ``mapping`` of url paths to request handlers.
"""

from bootstrap import Bootstrap
from view import *


mapping = [(
        r'/',
        Index
    ), (
        r'/standard\/?',
        Standard
    ), (
        r'/download\/?',
        Download
    ), (
        r'/support\/?',
        Support
    ), (
        r'/contact\/?',
        Contact
    ), (
        r'/library\/?',
        Library
    ), (
        r'/library/add_design\/?',
        AddDesign
    ), (
        r'/library/add_design/success\/?',
        AddDesignSuccess
    ), (
        r'/library/series/(\w+)\/?',
        Series
    ), (
        r'/library/design/([0-9]+)\/?',
        Design
    ), (
        r'/bootstrap\/?',
        Bootstrap
    ), (
        r'/.*',
        NotFound
    )
]
