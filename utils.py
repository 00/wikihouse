# -*- coding: utf-8 -*-

"""Utility functions."""

import logging

from json import loads as decode_json

from google.appengine.api import memcache
from google.appengine.api.urlfetch import fetch as urlfetch, POST
from google.appengine.ext import db

def render_number_with_commas(n):
    result = ''
    while n >= 1000:
        n, r = divmod(n, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (n, result)

def get_exchange_rate_to_gbp(currency, cache={}):
    if currency == 'GBP':
        return 1
    if currency in cache:
        return cache[currency]
    rate = memcache.get('exchange:%s' % currency)
    if rate:
        return cache.setdefault(currency, rate)
    url = "https://rate-exchange.appspot.com/currency?from=%s&to=GBP" % currency
    try:
        rate = float(decode_json(urlfetch(url).content)['rate'])
    except Exception, err:
        logging.error("currency conversion: %s" % err)
        return 0
    memcache.set('exchange:%s' % currency, rate)
    return cache.setdefault(currency, rate)

