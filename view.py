#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ``RequestHandler``s.
"""

from __future__ import with_statement

import base64
import cgi
import gettext
import logging
import urllib

from pytz.gae import pytz
from xml.etree import ElementTree as etree

from google.appengine.api import files, images, mail, memcache, users
from google.appengine.ext import blobstore, db

from weblayer import RequestHandler as BaseRequestHandler
from weblayer.utils import encode_to_utf8, unicode_urlencode
from weblayer.utils import json_decode, json_encode, xhtml_escape

import auth
import model

class RequestHandler(BaseRequestHandler):
    """ Adds i18n and SketchUp awareness support to `weblayer.RequestHandler`:
      
      * providing `self._` and passing `_()` through to templates
      * provide `self.country_code` by setting a `country_code` cookie
      * providing `self.is_sketchup` and passing `is_sketchup` to templates
      
    """
    
    def _get_accepted_languages(self):
        """ Return a list of language tags sorted by their "q" values.
        """
        
        header = self.request.headers.get('Accept-Language', None)
        if header is None:
            return []
        langs = [v for v in header.split(",") if v]
        qs = []
        for lang in langs:
            pieces = lang.split(";")
            lang, params = pieces[0].strip().lower(), pieces[1:]
            q = 1
            for param in params:
                if '=' not in param:
                    # Malformed request; probably a bot, we'll ignore
                    continue
                lvalue, rvalue = param.split("=")
                lvalue = lvalue.strip().lower()
                rvalue = rvalue.strip()
                if lvalue == "q":
                    q = float(rvalue)
            qs.append((lang, q))
        qs.sort(lambda a, b: -cmp(a[1], b[1]))
        return [lang for (lang, q) in qs]
        
    
    def render(self, tmpl_name, **kwargs):
        """ Pass `users` `quote` and `_` through to the template.
        """
        
        return super(RequestHandler, self).render(
            tmpl_name, 
            users=users, 
            quote=urllib.quote,
            _=self._, 
            is_sketchup=self.is_sketchup,
            **kwargs
        )
        
    
    def __init__(self, *args, **kwargs):
        super(RequestHandler, self).__init__(*args, **kwargs)
        # provide `self._` and passing `_()` through to templates
        localedir = self.settings.get('locale_directory')
        supported = self.settings.get('supported_languages')
        target = self.settings.get('default_language')
        for item in self._get_accepted_languages():
            # Convert `en-us` to `en`.
            item = item.split('-')[0]
            if item in supported:
                target = item
                break
        translation = gettext.translation(
            'wikihouse', 
            localedir=localedir, 
            languages=[target]
        )
        self._ = translation.ugettext
        # provide `self.country_code` by setting a `country_code` cookie
        cc = self.cookies.get('country_code')
        if cc is None or cc == 'zz':
            cc = self.request.headers.get('X-AppEngine-Country', 'GB').lower()
            self.cookies.set('country_code', cc, expires_days=None)
        self.country_code = cc
        # provide `self.is_sketchup`
        self.is_sketchup = self.cookies.get('is_sketchup') == 'true'
        
    
    


class Index(RequestHandler):
    """
    """
    
    def get(self):
        quotes = model.Quote.get_all()
        users_with_avatars = model.User.get_with_real_avatars()
        return self.render(
            'index.tmpl', 
            quotes=quotes, 
            users_with_avatars=users_with_avatars
        )
        
    
    


class About(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('about.tmpl')
        
    
    

class Guide(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('guide.tmpl')
        
    
    

class Download(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('download.tmpl')
        
    
    


class Donate(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('donate.tmpl')
        
    
    

class Collaborate(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('collaborate.tmpl')
        
    
    

class Contact(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('contact.tmpl')
        
    
    


class Terms(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('terms.tmpl')
        
    
    


class SketchupAwareHandler(RequestHandler):
    """ Looks for optional `sketchup\/?` at the end of the url.  If present sets
      a `is_sketchup` session cookie to be `true`.
      
      N.b.: this uses the url path and not a request param because the request
      param gets lost through the Google authentication redirect.
    """
    
    def __init__(self, *args, **kwargs):
        super(SketchupAwareHandler, self).__init__(*args, **kwargs)
        path = self.request.path
        if path.endswith('sketchup') or path.endswith('sketchup/'):
            self.cookies.set('is_sketchup', 'true', expires_days=None)
            self.is_sketchup = True
            
        
    
    


class Library(SketchupAwareHandler):
    """
    """
    
    def get(self, name=None):
        
        # Get all `Series` so we can populate the category navigation and
        # the target `Series` if one has been selected.
        series = model.Series.get_all()
        if name is None:
            target = None
        else:
            target = model.Series.get_by_key_name(name)
            if target is None:
                return self.error(status=404)
            
        # Get either the most recent 9 `Design`s or the `Design`s in the
        # target `Series`.
        if target is None:
            designs = model.Design.all_listings(limit=9)
        else:
            designs = target.designs
        
        # Render the template.
        return self.render(
            'library.tmpl', 
            series=series, 
            target=target, 
            designs=designs
        )
        
    
    


class AddDesign(SketchupAwareHandler):
    """
    """
    
    __all__ = ['get', 'post']
    
    _uploads = None
    _upload_files = {
        'model': 'application/vnd.sketchup.skp',
        'model_preview': 'image/jpeg',
        'model_preview_reverse': 'image/jpeg',
        'sheets': 'application/octet-stream', # XXX tbc
        'sheets_preview': 'image/jpeg'
    }
    
    def _write_file(self, mime_type, data):
        """ Write `data` to the blob store and return a blob key.
        """
        
        # Create the file
        file_name = files.blobstore.create(mime_type=mime_type)
        
        # Open the file and write to it
        with files.open(file_name, 'a') as f:
            while data:
                f.write(data[:921600])
                data = data[921600:]
        
        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)
        
        # Get the file's blob key
        return files.blobstore.get_blob_key(file_name)
        
    
    def _get_uploads(self):
        """ Lazy decode and store file uploads.  If we're handling an image,
          adds a `${key}_serving_url` string property.
        """
        
        if self._uploads is None:
            self._uploads = {}
            params = self.request.params
            for key, value in params.iteritems():
                if value and key in self._upload_files:
                    mime_type = self._upload_files.get(key)
                    data = base64.urlsafe_b64decode(encode_to_utf8(value))
                    blob_key = self._write_file(mime_type, data)
                    if mime_type.startswith('image'):
                        serving_key = '%s_serving_url' % key
                        serving_url = images.get_serving_url(blob_key)
                        self._uploads[serving_key] = serving_url
                    self._uploads[key] = blob_key
        return self._uploads
        
    
    
    def notify(self, design):
        """ Notify the moderators.  Note that we use the first email in the
          moderators list as the sender.
        """
        
        url = self.request.host_url
        user = users.get_current_user()
        recipient = user.email()
        sender = self.settings['moderator_email_address']
        subject = self._(u'New design submitted to WikiHouse')
        body = u'%s\n\n%s %s\n%s %s/library/design/%s\n\n%s\nWikiHouse\n%s\n' % (
            self._(u'Your design has been queued for moderation:'),
            self._(u'Title:'),
            xhtml_escape(design.title),
            self._(u'Url:'),
            url,
            design.key().id(),
            self._(u'Thanks,'),
            url
        )
        message = mail.EmailMessage(
            to=recipient,
            sender=sender, 
            subject=subject, 
            body=body
        )
        message.send()
        
    
    
    @auth.required
    def post(self):
        
        attrs = {}
        error = u''
        
        params = self.request.params
        uploads = self._get_uploads()
        
        attrs['title'] = params.get('title')
        attrs['description'] = params.get('description')
        
        series = params.getall('series')
        keys = [db.Key.from_path('Series', item) for item in series]
        instances = model.Series.get(keys)
        if None in instances:
            i = instances.index(None)
            error = u'Series `%s` does not exist.' % series[i]
        attrs['series'] = keys
        
        if not error:
            google_user = users.get_current_user()
            google_user_id = google_user.user_id()
            user = model.User.get_by_user_id(google_user_id)
            # If this user has not been stored yet, create and store it.
            if user is None:
                try:
                    user = model.User(
                        google_user=google_user,
                        google_user_id=google_user_id
                    )
                    user.put()
                except db.Error, err:
                    error = unicode(err)
                
        if not error:
            attrs['user'] = user.key()
            attrs['google_user_id'] = google_user_id
            attrs['component'] = params.get('component') == '1'
            attrs['verification'] = params.get('verification')
            attrs['notes'] = params.get('notes')
            attrs['sketchup_version'] = params.get('sketchup_version')
            attrs['plugin_version'] = params.get('plugin_version')
            
            # If the current user is an admin, skip moderation.
            if users.is_current_user_admin():
                attrs['status'] = u'approved'
            
            country_code = self.country_code
            try:
                country = pytz.country_names[country_code.lower()]
            except KeyError:
                country = country_code
            attrs['country'] = country
            
            attrs.update(uploads)
            try:
                design = model.Design(**attrs)
                design.put()
            except db.Error, err:
                error = unicode(err)
        
        if error:
            data = unicode_urlencode({'error': error})
            response = self.redirect('/library/add_design/error?%s' % data)
        else:
            response = self.redirect('/library/add_design/success/%s' % design.key().id())
            # Notify design will be moderated, unless the current user is an admin.
            if not users.is_current_user_admin():
                self.notify(design)
            
        response.body = ''
        return response
        
    
    
    @auth.required
    def get(self):
        series = model.Series.get_all()
        upload_url = blobstore.create_upload_url(self.request.path)
        return self.render('add.tmpl', upload_url=upload_url, series=series)
        
    
    

class AddDesignSuccess(RequestHandler):
    """
    """
    
    @auth.required
    def get(self, id):
        path = '/library/design/%s' % id
        return {'success': path}
        
    
    

class AddDesignError(RequestHandler):
    """
    """
    
    @auth.required
    def get(self):
        message = self.request.params.get('error')
        return {'error': message}
        
    
    


class Moderate(RequestHandler):
    
    __all__ = ['get', 'post']
    
    def notify(self, design, user):
        """ Notify the design's user that they need to register their email with
          gravatar.
        """
        
        url = self.request.host_url
        recipient = user.email
        sender = self.settings['moderator_email_address']
        subject = self._(u'Complete your WikiHouse profile with a gravatar')
        body = u'%s\n\n%s %s\n%s %s/library/design/%s\n\n%s\n\n%s%s\n\n%s\nWikiHouse\n%s\n' % (
            self._(u'Your design has been approved and included in the WikiHouse library:'),
            self._(u'Title:'),
            xhtml_escape(design.title),
            self._(u'Url:'),
            url,
            design.key().id(),
            self._(u'To complete your user profile and have your design featured, register a profile image against your email address here:'),
            'http://en.gravatar.com/site/signup/',
            urllib.quote(user.email),
            self._(u'Thanks,'),
            url
        )
        logging.info(body)
        message = mail.EmailMessage(
            to=recipient,
            sender=sender, 
            subject=subject, 
            body=body
        )
        message.send()
        
    
    
    @auth.admin
    def post(self):
        params = self.request.params
        action = params.get('action')
        design = model.Design.get_by_id(int(params.get('id')))
        if action == self._(u'Approve'):
            design.status = u'approved'
            user = design.user
            # If this user doesn't have their avatar set, set it.
            if not user.avatar:
                user.set_avatar()
            # Save / touch to update the modified datetime.
            try:
                user.put()
            except db.Error, err:
                error = unicode(err)
            # If the user doesn't have a real avatar, notify them
            if not user.has_real_avatar:
                self.notify(design, user)
        elif action == self._('Reject'):
            design.status = u'rejected'
        design.put()
        return self.get()
        
    
    
    @auth.admin
    def get(self):
        query = model.Design.all().filter("status =", u'pending')
        designs = query.order('-m').fetch(99)
        return self.render('moderate.tmpl', designs=designs)
    
    


class Design(RequestHandler):
    """
    """
    
    def get(self, id):
        target = model.Design.get_by_id(int(id))
        if target is None:
            return self.error(status=404)
        series = model.Series.get_all()
        developer = self.settings['dev'] or 'appspot.com' in self.request.host
        return self.render(
            'design.tmpl', 
            target=target, 
            series=series,
            disqus_developer=developer
        )
        
    
    


class Users(RequestHandler):
    """ 
    """
    
    def get(self):
        contributors = model.User.get_all()
        return self.render('users.tmpl', contributors=contributors)
        
    
    


class User(RequestHandler):
    """ 
    """
    
    def get(self, id):
        target = model.User.get_by_id(int(id))
        if target is None:
            return self.error(status=404)
        designs = target.designs
        return self.render('user.tmpl', target=target, designs=designs)
        
    
    


class Base64Blob(RequestHandler):
    """
    """
    
    def get(self, key):
        response = self.response
        key = str(urllib.unquote(key))
        blob_info = blobstore.BlobInfo.get(key)
        response.headers['Content-Type'] = blob_info.content_type
        blob_reader = blob_info.open(buffer_size=921600)
        while 1:
            chunk = blob_reader.read(921600)
            if chunk:
                value = base64.b64encode(chunk)
                response.body_file.write(value)
            else:
                break
        blob_reader.close()
        return response
        
    
    


class MessageStrings(RequestHandler):
    """ Return a translated dictionary of message strings using the keys
      in `/static/build/js/message_strings.json`.
    """
    
    def get(self):
        data = {}
        for k in self.settings.get('js_message_strings'):
            data[k] = self._(k)
        self.response.headers['Content-Type'] = 'text/javascript'
        self.response.charset = 'utf8'
        return u'window.message_strings = %s;' % json_encode(data)
        
    
    


class ActivityFeed(RequestHandler):
    """ Consume the latest Disqus comments and convert into a feed with design
      and user images.
    """
    
    def get(self):
        """ Get Disqus feed.  Loop through.  Get user and model images for
          each comment.  Turn into an RSS feed.  Cache for 5 mins.
        """
        
        # Cache the response for 5 minutes.
        CACHE_KEY = 'feeds:activity'
        CACHE_TIME = 60 * 5
        
        feed = memcache.get(CACHE_KEY)
        if feed is None:
            
            # get the Disque feed
            sock = urllib.urlopen('http://wikihouse.disqus.com/latest.rss')
            text = sock.read()
            sock.close()
            
            # Build a list of items.
            items = []
            tree = etree.fromstring(text)
            last_build_date = tree.find('channel/lastBuildDate').text
            for item in tree.findall('channel/item'):
                
                # Add the creator as an item.
                creator = item.find('{http://purl.org/dc/elements/1.1/}creator').text
                items.append({
                        'title': creator,
                        'description': item.find('description').text,
                        'link': u'http://disqus.com/api/users/avatars/%s.jpg' % creator
                })
                
                # Add the design as an item.
                link = item.find('link').text
                design_id = link.split('/')[-1].split('#')[0]
                design = model.Design.get_by_id(int(design_id))
                if design and design.model_preview:
                    link = u'%s/blob/%s/%s.png' % (
                        self.request.host_url,
                        design.model_preview.key(),
                        urllib.quote(design.title)
                    )
                    items.append({
                            'title': design.title,
                            'description': design.description,
                            'link': link
                    })
            
            # Render the feed and cache the output.
            feed = self.render(
                'rss/activity.tmpl', 
                items=items, 
                last_build_date=last_build_date
            )
            memcache.set(CACHE_KEY, feed, time=CACHE_TIME)
        
        # Return the response.
        self.response.headers['Content-Type'] = 'application/xml'
        self.response.charset = 'utf8'
        return feed
        
    
    


class NotFound(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('errors/404.tmpl')
        
    
    


