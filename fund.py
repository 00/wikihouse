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

from view import RequestHandler

create_key = db.Key.from_path

CAMPAIGNS = [
    ('sketchup', 500000, 'SketchUp Extension', 'Blah blah blah'),
    ('hardware', 25000000, 'Hardware Designs', 'More blah blah'),
    ('platform', 18000000, 'Platform Development', 'Even more blah'),
]

CAMPAIGN_KEYS = {}

for _campaign in CAMPAIGNS:
    CAMPAIGN_KEYS[_campaign[0]] = create_key('Campaign', _campaign[0])
del _campaign

CURRENCIES = frozenset(['GBP', 'EUR', 'USD'])
ENDPOINT = 'https://www.sandbox.paypal.com/uk/cgi-bin/webscr'
PAYPAL_ACCOUNT = 'hello-facilitator@wikihouse.cc'
PAYPAL_LOGO_IMAGE = 'https://s3-eu-west-1.amazonaws.com/thruflo-random-stuff/wikihouse_header.png'
NOTIFY_URL = 'https://wikihouse-cc.appspot.com/ipn'
THANK_YOU_URL = 'https://wikihouse-cc.appspot.com/thank-you'

class Campaign(db.Model):
    """Appengine model class encapsultating a fundable campaign.
      
      The key is the campaign id.
    """
    
    v = db.IntegerProperty(default=0)             # version 
    c = db.DateTimeProperty(auto_now_add=True)    # created
    m = db.DateTimeProperty(auto_now=True)        # modified
    
    funder_count = db.IntegerProperty(default=0)
    total_gbp = db.IntegerProperty(default=0)
    total_eur = db.IntegerProperty(default=0)
    total_usd = db.IntegerProperty(default=0)

class PayPalTransaction(db.Model):
    """Appengine model class encapsultating a donation made to a campaign.
      
      The key is the paypal transaction id.
    """
    
    v = db.IntegerProperty(default=0)
    c = db.DateTimeProperty(auto_now_add=True)
    m = db.DateTimeProperty(auto_now=True)
    
    campaign_id = db.StringProperty(default='', indexed=False)
    payer_email = db.StringProperty(default='', indexed=False)
    fee = db.StringProperty(default='', indexed=False)
    gross = db.StringProperty(default='', indexed=False)
    is_handled = db.BooleanProperty(default=False)
    info_payload = db.TextProperty()
    net = db.StringProperty(default='', indexed=False)
    payer_name = db.StringProperty(default='', indexed=False)
    currency = db.StringProperty(default='', indexed=False)

class TransactionReceipt(db.Model):
    """Stub entity to synchronise accounted transactions.
      
      The parent is the campaign_key, key is the txn_key.
    """


class InstantPaymentNotificationHandler(RequestHandler):
    """Handle `Instant Payment Notifications`_ from PayPal.
      
      _`Instant Payment Notifications`: http://bit.ly/11tmE50
    """
    
    #__all__ = ['post']
    __all__ = ['post', 'get', 'head']
    
    check_xsrf = False
    
    def get(self):
        """Render the form, just to see if it works."""
        
        return gen_fund_form()
    
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
    url = "http://rate-exchange.appspot.com/currency?from=%s&to=GBP" % currency
    try:
        rate = decode_json(urlfetch(url).content)['rate']
    except Exception, err:
        logging.error("currency conversion: %s" % err)
        return 0
    memcache.set('exchange:%s' % currency, rate)
    return cache.setdefault(currency, rate)

def gen_fund_form():
    html = []; out = html.append
    entities = {}
    for campaign_id in sorted(CAMPAIGN_KEYS):
        campaign_key = CAMPAIGN_KEYS[campaign_id]
        campaign = Campaign.get(campaign_key)
        if campaign is None:
            campaign = Campaign(key=campaign_key)
            campaign.put()
        entities[campaign.key().name()] = campaign
    for campaign in CAMPAIGNS:
        campaign_id = campaign[0]
        ent = entities[campaign_id]
        if ent.funder_count == 1:
            backers = '1 Backer'
        else:
            backers = '%d Backers' % ent.funder_count
        target = campaign[1]
        total = ent.total_gbp
        if ent.total_eur:
            total += (ent.total_eur * get_exchange_rate_to_gbp('EUR'))
        if ent.total_usd:
            total += (ent.total_usd * get_exchange_rate_to_gbp('USD'))
        raised = int(total)
        if raised >= target:
            pct = 100
        else:
            pct = (raised * 100)/target
        kwargs = dict(
            action=ENDPOINT,
            backers=backers,
            campaign=campaign_id,
            email=PAYPAL_ACCOUNT,
            image=PAYPAL_LOGO_IMAGE,
            info=escape(campaign[3]),
            notify_url=NOTIFY_URL,
            thank_you_url=THANK_YOU_URL,
            pct=pct * 1, # multiply by 2 if width == 200px, etc.
            raised=render_number_with_commas(raised/100),
            target=render_number_with_commas(target/100),
            title=escape(campaign[2])
            )
        out("""<div class="campaign">
      <div class="campaign-title">%(title)s</div>
      <div class="campaign-info">%(info)s</div>
      <div class="campaign-backers">%(backers)s</div>
      <div class="campaign-raised">Raised: £%(raised)s</div>
      <div class="campaign-target">%(pct)s%% of target £%(target)s</div>
      <form action="%(action)s" method="post">
        <input type="text" name="amount" value="" placeholder="Amount, e.g. 30.00" />
        <input type="hidden" name="business" value="%(email)s" />
        <input type="hidden" name="cancel_return" value="http://www.wikihouse.cc/" />
        <input type="hidden" name="charset" value="utf-8" />
        <input type="hidden" name="cmd" value="_donations" />
        <input type="hidden" name="custom" value="wikihouse.%(campaign)s" />
        <input type="hidden" name="image_url" value="%(image)s" />
        <input type="hidden" name="item_name" value="Fund WikiHouse" />
        <input type="hidden" name="item_number" value="wikihouse.%(campaign)s" />
        <input type="hidden" name="no_note" value="1" />
        <input type="hidden" name="notify_url" value="%(notify_url)s" />
        <input type="hidden" name="return" value="%(thank_you_url)%" />
        <input type="hidden" name="rm" value="1" />
        <select name="currency_code">
          <option value="GBP">British Pounds (£)</option>
          <option value="EUR">Euros (€)</option>
          <option value="USD">US Dollars ($)</option>
        </select>
        <input type="submit" name="submit" value=" Back This! ">
      </form>
    </div>""" % kwargs)
    return ''.join(html)

