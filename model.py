#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Database ``Model`` classes.
"""

import itertools
import hashlib
import logging
import urllib
import urllib2

from google.appengine.api import users
from google.appengine.ext import blobstore, db

from weblayer.utils import json_decode

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
            hash_ = hashlib.md5(self.email.strip().lower()).hexdigest()
            # Using `d=mm` to fallback on the "mystery man" image if no gravatar
            # is found.
            avatar = 'http://www.gravatar.com/avatar/%s?s=%s&d=mm' % (hash_, size)
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
    
    
    component = db.BooleanProperty(required=True, default=False)
    title = db.StringProperty(required=True)
    description = db.TextProperty(required=True)
    series = db.ListProperty(db.Key)
    
    user = db.ReferenceProperty(User)
    google_user_id = db.StringProperty()
    country = db.StringProperty()                       # X-AppEngine-Country
    
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
    
    model = blobstore.BlobReferenceProperty()
    model_preview = blobstore.BlobReferenceProperty()
    model_preview_reverse = blobstore.BlobReferenceProperty()
    sheets = blobstore.BlobReferenceProperty()
    sheets_preview = blobstore.BlobReferenceProperty()
    
    @classmethod
    def all_listings(cls, filter_by=None, limit=99):
        """ Return all designs that are either approved or by the current user.
        """
        
        google_user = users.get_current_user()
        google_user_id = google_user and str(google_user.user_id()) or ''
        
        # Get the approved designs.
        query = cls.all().order('-m')
        if filter_by is not None:
            for k, v in filter_by:
                query.filter(k, v)
        approved = query.filter("status =", u'approved')
        approved_results = approved.fetch(limit)
        
        # Get the user's designs.
        query = cls.all().order('-m')
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
    
    @classmethod
    def get_all(cls):
        return cls.all().order('m')
        
    
    


