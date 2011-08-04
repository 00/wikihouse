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
        r'/standard',
        Standard
    ), (
        r'/download',
        Download
    ), (
        r'/support',
        Support
    ), (
        r'/contact',
        Contact
    ), (
        r'/library',
        Library
    ), (
        r'/bootstrap\/?',
        Bootstrap
    ), (
        r'/.*',
        NotFound
    )
]
