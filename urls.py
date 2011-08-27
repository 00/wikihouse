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
        r'/legal/terms',
        Terms
    ), (
        r'/library\/?',
        Library
    ), (
        r'/library/sketchup\/?',
        Library
    ), (
        r'/library/series/(\w+)\/?',
        Library
    ), (
        r'/library/users\/?',
        Users
    ), (
        r'/library/users/([0-9]+)\/?',
        User
    ), (
        r'/library/designs/([0-9]+)\/?',
        Design
    ), (
        r'/library/add_design\/?',
        AddDesign
    ), (
        r'/library/add_design/sketchup\/?',
        AddDesign
    ), (
        r'/library/add_design/success/([0-9]+)\/?',
        AddDesignSuccess
    ), (
        r'/library/add_design/error\/?',
        AddDesignError
    ), (
        r'/admin/moderate\/?',
        Moderate
    ), (
        r'/admin/bootstrap\/?',
        Bootstrap
    ), (
        r'/blob64/([^/]+)/([^/]+)\/?',
        Base64Blob
    ), (
        r'/blob64/([^/]+)\/?',
        Base64Blob
    ), (
        r'/i18n/message_strings.json',
        MessageStrings
    ), (
        r'/feeds/activity.rss',
        ActivityFeed
    ), (
        r'/.*',
        NotFound
    )
]
