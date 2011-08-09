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
        r'/about\/?',
        About
    ), (
        r'/guide\/?',
        Guide
    ), (
        r'/download\/?',
        Download
    ), (
        r'/donate\/?',
        Donate
    ), (
        r'/collaborate\/?',
        Collaborate
    ), (
        r'/contact\/?',
        Contact
    ), (
        r'/library\/?',
        Library
    ), (
        r'/library/series/(\w+)\/?',
        Library
    ), (
        r'/library/design/([0-9]+)\/?',
        Design
    ), (
        r'/library/add_design\/?',
        AddDesign
    ), (
        r'/library/add_design/success/([0-9]+)\/?',
        AddDesignSuccess
    ), (
        r'/library/add_design/error\/?',
        AddDesignError
    ), (
        r'/moderate\/?',
        Moderate
    ), (
        r'/bootstrap\/?',
        Bootstrap
    ), (
        r'/blob64/([^/]+)?',
        Base64Blob
    ), (
        r'/.*',
        NotFound
    )
]
