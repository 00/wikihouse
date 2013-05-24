#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Database ``Model`` classes.
"""

import itertools
import hashlib
import logging
import urllib
import urllib2

from cgi import escape

from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import db

from weblayer.utils import json_decode

from utils import get_exchange_rate_to_gbp
from utils import render_number_with_commas

CAMPAIGNS = [(
        'sketchup',
        12000,
        'SketchUp',
        'Plugin',
        'SketchUp Plugin',
        'Completing the WikiHouse SketchUp plugin to allow full one-click automation;\
        laying out parts onto sheets, naming them correctly and exporting a\
        .dxf cutting file.'
    ), (
        'hardware', 
        240000, 
        'Hardware',
        'Full House', 
        'Hardware',
        'Design, construct and document the first full WikiHouse - completed, tested\
        and lived-in, with designs, instructions and costings shared openly online,\
        so anyone can build it for themselves.'
    ), (
        'platform',
        240000,
        'WikiHouse',
        'Platform',
        'Platform',
        "Help create the Wikipedia of things. Use it to easily create and customize\
        designs right within your browser, get them made to your liking, and\
        be rewarded as part of the sharing economy!"
    )
]

CAMPAIGN_KEYS = {}

for _item in CAMPAIGNS:
    CAMPAIGN_KEYS[_item[0]] = db.Key.from_path('Campaign', _item[0])
del _item

class User(db.Model):
    """ Encapsulate a `User`, wrap the `google.appengine.api.users.User` with
      some additional properties.
    """
    
    v = db.IntegerProperty(default=1)                   # version
    c = db.DateTimeProperty(auto_now_add=True)          # created
    m = db.DateTimeProperty(auto_now=True)              # modified
    
    google_user = db.UserProperty()
    google_user_id = db.StringProperty()
    
    avatar = db.StringProperty()
    has_real_avatar = db.BooleanProperty(default=False)
    
    @property
    def id(self):
        return self.key().id()
        
    
    
    @property
    def nickname(self):
        return self.google_user.nickname()
        
    
    
    @property
    def email(self):
        return self.google_user.email()
        
    
    
    @classmethod
    def get_by_user_id(cls, user_id):
        user_id = str(user_id)
        query = cls.all().filter('google_user_id =', user_id)
        return query.get()
        
    
    
    @classmethod
    def get_all(cls):
        return cls.all().order('-m')
        
    
    
    @classmethod
    def get_with_real_avatars(cls, limit=40):
        query = cls.all().filter('has_real_avatar =', True)
        return query.order('-m').fetch(limit)
        
    
    
    @property
    def designs(self):
        return Design.all_listings(filter_by=[("user =", self.key())])
        
    
    
    def get_gravatar(self, size=80):
        """ Get URL to gravatar image, using `d=mm` to fallback on the 
          "mystery man" image if no gravatar is registered.
        """
        
        hash_ = hashlib.md5(self.email.strip().lower()).hexdigest()
        return 'https://secure.gravatar.com/avatar/%s?s=%s&d=mm' % (hash_, size)
    
    def set_avatar(self, size=80):
        """ Try and scrape the profile image from Google+ using YQL, falling back
          on `Gravatar`_ if this fails.
          
          The scrape hack relies on either `https://profiles.google.com/${username}`
          or `http://gplus.to/${username}` redirecting to the right Google+ url.
          
          _`Gravatar`: http://en.gravatar.com/site/implement/images/
        """
        
        avatar = None
        has_real_avatar = False
        
        # If we can get a google username from the email (quite likely) then try
        # scraping the profile image from Google+ (nasty).
        google_username = None
        parts = self.nickname.split('@')
        if len(parts) == 1:
            google_username = self.nickname
        elif parts[1] == 'gmail.com' or parts[1] == 'googlemail.com':
            google_username = parts[0]
        
        if google_username is not None:
            urls = [
                'https://profiles.google.com/%s' % google_username,
                'http://gplus.to/%s' % google_username
            ]
            for url in urls:
                # Build YQL query.
                table = 'http://yqlblog.net/samples/data.html.cssselect.xml'
                what = 'data.html.cssselect'
                query = 'use "%s" as %s; select * from %s where url="%s" and css=".photo"' % (
                    table,
                    what,
                    what,
                    url
                )
                # Make YQL query.
                sock = urllib.urlopen(
                    'https://query.yahooapis.com/v1/public/yql',
                    data=urllib.urlencode({'q': query, 'format': 'json'})
                )
                text = sock.read()
                sock.close()
                # Parse the response.
                data = json_decode(text)
                results = data['query']['results']['results']
                if results is not None:
                    src = results['img']['src']
                    avatar = src.replace('?sz=200', '?sz=%s' % size)
                    has_real_avatar = True
                    break
                
        # Fall back on Gravatar.
        if avatar is None:
            avatar = self.get_gravatar(size=size)
            # Calling the thing with `d=404` to determine whether the avatar is real
            # or not.
            try:
                sock = urllib2.urlopen(avatar.replace('&d=mm', '&d=404'))
            except urllib2.URLError, e:
                has_real_avatar = False
            else:
                has_real_avatar = True
            
        # Set `self.avatar`.
        self.avatar = avatar
        self.has_real_avatar = has_real_avatar
        
    
    

class Series(db.Model):
    """ A WikiHouse standard design series.
    """
    
    v = db.IntegerProperty(default=1)                   # version
    c = db.DateTimeProperty(auto_now_add=True)          # created
    m = db.DateTimeProperty(auto_now=True)              # modified
    
    order = db.IntegerProperty()
    title = db.StringProperty()
    description = db.TextProperty(default='')
    
    @classmethod
    def get_all(cls):
        return cls.all().order('order')
        
    
    
    @property
    def designs(self):
        return Design.all_listings(filter_by=[("series =", self.key())])
        
    
    

class Design(db.Model):
    """ A design in the WikiHouse library.
    """
    
    v = db.IntegerProperty(default=1)                   # version
    c = db.DateTimeProperty(auto_now_add=True)          # created
    m = db.DateTimeProperty(auto_now=True)              # modified
    
    deleted = db.BooleanProperty(required=True, default=False)
    
    component = db.BooleanProperty(required=True, default=False)
    title = db.StringProperty(required=True)
    description = db.TextProperty(required=True)
    url = db.LinkProperty()
    series = db.ListProperty(db.Key)
    
    user = db.ReferenceProperty(User)
    google_user_id = db.StringProperty()
    country = db.StringProperty()                       # X-AppEngine-Country
    
    grid = db.StringProperty(
        choices=[
            u'450mm', 
            u'550mm', 
            u'600mm',
            u'900mm',
            u'other'
        ],
        default=u'550mm'
    )
    status = db.StringProperty(
        choices=[
            u'pending', 
            u'approved', 
            u'rejected'
        ],
        default=u'pending'
    )
    verification = db.StringProperty(
        choices=[
            u'unverified', 
            u'verified', 
            u'built'
        ],
        default=u'unverified'
    )
    notes = db.TextProperty()
    sketchup_version = db.StringProperty()
    plugin_version = db.StringProperty()
    
    model = blobstore.BlobReferenceProperty()
    model_preview = blobstore.BlobReferenceProperty()
    model_preview_reverse = blobstore.BlobReferenceProperty()
    model_preview_serving_url = db.StringProperty()
    model_preview_reverse_serving_url = db.StringProperty()
    sheets = blobstore.BlobReferenceProperty()
    sheets_preview = blobstore.BlobReferenceProperty()
    embeddable_sheets_preview = blobstore.BlobReferenceProperty()
    
    @classmethod
    def all_listings(cls, filter_by=None, limit=99):
        """ Return all designs that are either approved or by the current user.
        """
        
        google_user = users.get_current_user()
        google_user_id = google_user and str(google_user.user_id()) or ''
        
        # Get the approved designs.
        query = cls.all().order('-m').filter("deleted =", False)
        if filter_by is not None:
            for k, v in filter_by:
                query.filter(k, v)
        approved = query.filter("status =", u'approved')
        approved_results = approved.fetch(limit)
        
        # Get the user's designs.
        query = cls.all().order('-m').filter("deleted =", False)
        if filter_by is not None:
            for k, v in filter_by:
                query.filter(k, v)
        owned_results = []
        if google_user is not None:
            owned = query.filter("google_user_id =", google_user_id)
            owned_results = owned.fetch(limit)
        
        # Merge the two.
        if len(owned_results) == 0:
            results = approved_results
        else:
            chained = itertools.chain(approved_results, owned_results)
            results = dict((str(item.key()), item) for item in chained).values()
        
        # Sorting by modified date.
        results = sorted(results, key=lambda item: item.m)
        results.reverse()
        
        return results[:limit]
        
    
    

class Quote(db.Model):
    """ A press quote, uses `org` as key name.
    """
    
    v = db.IntegerProperty(default=1)                   # version
    c = db.DateTimeProperty(auto_now_add=True)          # created
    m = db.DateTimeProperty(auto_now=True)              # modified
    
    name = db.StringProperty()
    content = db.TextProperty(default='')
    href = db.LinkProperty()
    
    @classmethod
    def get_all(cls):
        return cls.all().order('m')
        
    
    

class Avatars(db.Model):
    """
    """
    
    twitter_followers = db.StringListProperty(indexed=False)
    disqus_commenters = db.StringListProperty(indexed=False)
    


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
    
    @classmethod
    def get_campaign_items(cls):
        """Return a list of campaign data where the dict keys are the campaign
          instance key names and the data is:
          
              [
                {
                  'category': 'software',
                  'title': 'Plugin',
                  'description': '...',
                  'num_backers': 32,
                  'percentage_raised': 50, # always an int
                  'total_raised': 5000,
                  'target': 10000
                },
                ...
              ]
          
        """
        
        # We build an items list as return value.
        items = []
        
        # Get the campaigns from the db -- creating them if they
        # don't exist.
        entities = {}
        
        def get_or_insert(campaign_id):
            """We do this manually rather than use Model.get_or_insert
              because otherwise we get keys generated that DONT MATCH
              THE ``CAMPAIGN_KEYS`` CREATED AT MODULE IMPORT TIME.
            """
            
            campaign_key = CAMPAIGN_KEYS[campaign_id]
            campaign = Campaign.get(campaign_key)
            if campaign is None:
                campaign = Campaign(key=campaign_key)
                campaign.put()
            return campaign
        
        for campaign_id in CAMPAIGN_KEYS:
            campaign = db.run_in_transaction(get_or_insert, campaign_id)
            entities[campaign_id] = campaign
        
        # Iterate through the campaigns, building the data for the page.
        for campaign in CAMPAIGNS:
            campaign_id = campaign[0]
            ent = entities[campaign_id]
            target = campaign[1]
            total = ent.total_gbp
            if ent.total_eur:
                total += (ent.total_eur * get_exchange_rate_to_gbp('EUR'))
            if ent.total_usd:
                total += (ent.total_usd * get_exchange_rate_to_gbp('USD'))
            raised = int(total/100)
            if raised >= target:
                pct = 100
            else:
                pct = (raised * 100) / target
            item = dict(
                category=campaign_id,
                title1=escape(campaign[2]),
                title2=escape(campaign[3]),
                title3=escape(campaign[4]),
                description=escape(campaign[5]),
                num_backers=ent.funder_count,
                percentage_raised=pct * 1,
                total_raised=render_number_with_commas(raised),
                target=render_number_with_commas(target)
            )
            items.append(item)
        return items
    


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

