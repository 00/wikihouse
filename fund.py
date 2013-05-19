#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Accept donations via PayPal and get the data back to display progress
  against funding targets.
  
  Transposed from https://gist.github.com/tav/5589012#file-fund-wikihouse-py
"""

import logging

from cgi import escape
from decimal import Decimal
from json import loads as decode_json

from google.appengine.api import memcache
from google.appengine.api.urlfetch import fetch as urlfetch, POST
from google.appengine.ext import db

from weblayer import RequestHandler

from model import CAMPAIGNS
from model import CAMPAIGN_KEYS
from model import Campaign
from model import PayPalTransaction
from model import TransactionReceipt
from utils import get_exchange_rate_to_gbp
from utils import render_number_with_commas

create_key = db.Key.from_path

CURRENCIES = frozenset(['GBP', 'EUR', 'USD'])
ENDPOINT = 'https://www.paypal.com/uk/cgi-bin/webscr'
PAYPAL_ACCOUNT = 'hello@wikihouse.cc'
PAYPAL_LOGO_IMAGE = 'https://s3-eu-west-1.amazonaws.com/thruflo-random-stuff/wikihouse_header.png'
NOTIFY_URL = 'https://wikihouse-cc.appspot.com/ipn'
THANK_YOU_URL = 'https://wikihouse-cc.appspot.com/thank-you'
CANCEL_URL = 'http://www.wikihouse.cc'

class InstantPaymentNotificationHandler(RequestHandler):
    """Handle `Instant Payment Notifications`_ from PayPal.
      
      _`Instant Payment Notifications`: http://bit.ly/11tmE50
    """
    
    __all__ = ['post']
    
    check_xsrf = False
    
    def post(self):
        """Pass the ``post_body`` and the parsed POST params as ``kwargs`` to
          the ``do_actual_ipn_handling`` function.
        """
        
        request = self.request
        response = do_actual_ipn_handling(request.body, request.POST)
        if response != "OK":
            logging.info("IPN RETCODE: %s" % response)
        return response
    

class ThankYouHandler(RequestHandler):
    """Redirect to the community page on the main url."""
    
    __all__ = ['get', 'head']
    
    def get(self):
        """Render the form, just to see if it works."""
        
        request = self.request
        url = request.host_url
        if request.host_url.endswith('appspot.com'):
            url = 'http://www.wikihouse.cc'
        path = 'community'
        return self.redirect('{0}/{1}'.format(url, path))
    


def do_actual_ipn_handling(payload, kwargs):
    if kwargs['payment_status'] != 'Completed':
        return '1'
    verification_payload = 'cmd=_notify-validate&' + payload
    resp = urlfetch(url=ENDPOINT, method=POST, payload=verification_payload)
    if resp.content != 'VERIFIED':
        return '2'
    campaign = kwargs['custom']
    if not campaign:
        return '3'
    if not campaign.startswith('wikihouse.'):
        return '4'
    campaign_id = campaign.split('.', 1)[1].strip()
    if campaign_id not in CAMPAIGN_KEYS:
        return '5'
    receiver = kwargs['receiver_email']
    if receiver != PAYPAL_ACCOUNT:
        return '6'
    currency = kwargs['mc_currency']
    if currency not in CURRENCIES:
        return '7'
    gross = kwargs['mc_gross']
    fee = kwargs['mc_fee']
    gross_d = Decimal(gross)
    fee_d = Decimal(fee)
    net = gross_d - fee_d
    if net <= 0:
        return '8'
    txn_id = kwargs['txn_id']
    first_name = kwargs.get('first_name')
    if first_name:
        first_name += ' '
    payer_name = (first_name + kwargs.get('last_name', '')).strip()
    payer_email = kwargs['payer_email']
    txn = PayPalTransaction.get_or_insert(
        key_name=txn_id,
        campaign_id=campaign_id,
        payer_email=payer_email,
        fee=fee, 
        gross=gross,
        info_payload=payload,
        net=str(net),
        payer_name=payer_name,
        currency=currency
    )
    campaign_key = CAMPAIGN_KEYS[campaign_id]
    campaign = Campaign.get(campaign_key)
    db.run_in_transaction(update_campaign_tallies, campaign, txn_id,
            currency, net)
    txn.is_handled = True
    txn.put()
    return 'OK'

def update_campaign_tallies(campaign, txn_id, currency, amount):
    amount_in_pence = int(amount * 100)
    campaign_key = campaign.key()
    receipt = db.get(create_key('TransactionReceipt', txn_id, parent=campaign_key))
    if receipt:
        return
    receipt = TransactionReceipt(key_name=txn_id, parent=campaign_key)
    campaign.funder_count += 1
    if currency == 'GBP':
        campaign.total_gbp += amount_in_pence
    elif currency == 'EUR':
        campaign.total_eur += amount_in_pence
    elif currency == 'USD':
        campaign.total_usd += amount_in_pence
    db.put([campaign, receipt])
    return

