#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides ``mapping`` of url paths to request handlers.
"""

from bootstrap import Bootstrap
from fund import InstantPaymentNotificationHandler
from fund import ThankYouHandler
from view import *

mapping = [(
        r'/',
        Index
    ), (
        r'/ipn',
        InstantPaymentNotificationHandler
    ), (
        r'/thank-you',
        ThankYouHandler
    ), (
        r'/about\/?',
        About
    ), (
        r'/guide\/?',
        Guide
    ), (
        r'/guide/download\/?',
        Download
    ), (
        r'/guide/standards\/?',
        Standards
    ), (
        r'/community\/?',
        Community
    ), (
        r'/support\/?',
        Support
    ), (
        r'/contact\/?',
        Contact
    ), (
        r'/press\/?',
        Press
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
        r'/library/designs/([0-9]+)/(edit)\/?',
        Design
    ), (
        r'/library/designs\/?',
        Design
    ), (
        r'/library/designs/add\/?',
        Design
    ), (
        r'/library/designs/add/sketchup\/?',
        Design
    ), (
        r'/redirect/success/([0-9]+)\/?',
        RedirectSuccess
    ), (
        r'/redirect/error\/?',
        RedirectError
    ), (
        r'/redirect/after/delete\/?',
        RedirectAfterDelete
    ),(
        r'/admin/moderate\/?',
        Moderate
    ), (
        r'/admin/bootstrap\/?',
        Bootstrap
    ), (
        r'/activity',
        ActivityScreen
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
        r'/.*',
        NotFound
    )
]
