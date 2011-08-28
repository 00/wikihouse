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
from google.appengine.api import datastore_errors
from google.appengine.ext import blobstore, db

from webob.exc import status_map, HTTPNotFound, HTTPForbidden

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
            target_language=self.target_language,
            remaining_languages=self.remaining_languages,
            is_sketchup=self.is_sketchup,
            **kwargs
        )
        
    
    def error(self, exception=None, status=500, **kwargs):
        """ Override weblayer default to render error messages using a nice
          template.
        """
        
        status = int(status)
        if exception is None:
            ExceptionClass = status_map[status]
            exception = ExceptionClass(**kwargs)
        response = self.request.get_response(exception)
        response.body = self.render(
            'error.tmpl', 
            title=exception.title,
            error=exception.explanation
        )
        return response
        
    
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
        self.target_language = target
        remaining = supported[:]
        remaining.remove(target)
        self.remaining_languages = remaining
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
        
    
    

class Design(SketchupAwareHandler):
    """ RESTful handler for a `model.Design`.
    """
    
    __all__ = ['head', 'get', 'post', 'put', 'delete']
    
    _uploads = None
    _upload_files = {
        'model': 'application/vnd.sketchup.skp',
        'model_preview': 'image/jpeg',
        'model_preview_reverse': 'image/jpeg',
        'sheets': 'image/vnd.dxf',
        'sheets_preview': 'image/jpeg'
    }
    
    @property
    def _disqus_dev_mode(self):
        is_dev_mode = self.settings['dev']
        is_dev_url = 'appspot.com' in self.request.host
        return is_dev_mode or is_dev_url
        
    
    
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
        
    
    def _send_notification(self, design):
        """ Notify the user and moderators that a design has been queued for
          moderation.
        """
        
        url = self.request.host_url
        user = users.get_current_user()
        recipient = user.email()
        sender = self.settings['moderator_email_address']
        subject = self._(u'New design submitted to WikiHouse')
        body = u'%s\n\n%s %s\n%s %s/library/designs/%s\n\n%s\nWikiHouse\n%s\n' % (
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
        
    
    def _ensure_edit_allowed(self, context):
        """ Ensure that the current user is allowed to edit the `context`.
        """
        
        current_user = users.get_current_user()
        is_user = current_user and current_user == context.user.google_user
        is_allowed = is_user or users.is_current_user_admin()
        if not is_allowed:
            raise HTTPForbidden
            
        
    
    def _redirect_on(self, id=None, error=None):
        """ Build a redirect response to return error data or success data.
          
          n.b.: We would return the data directly but add and edit forms used
          from the browser go via the blobstore upload machinery, which requires
          a redirect.
          
        """
        
        if error:
            data = unicode_urlencode({'error': error})
            path = '/redirect/error?%s' % data
        else:
            path = '/redirect/success/%s' % id
        
        response = self.redirect(path)
        response.body = ''
        
        return response
        
    
    
    def _get_context(self, id):
        """ Get the `model.Design` instance with the provided `id`.
          
          If no `id`, returns `None`.  Otherwise if there's no design with that
          `id`, raises a 404.
          
        """
        
        if id is not None:
            context = model.Design.get_by_id(int(id))
            if context is None or context.deleted:
                raise HTTPNotFound
            return context
            
        
    
    def _get_uploads(self):
        """ Lazy decode and store file uploads from either:
          
          * base64 encoded form body data
          * the app engine blob store upload_url machinery
          
          If we're handling an image, adds a `${key}_serving_url` string property.
          
        """
        
        if self._uploads is None:
            self._uploads = {}
            params = self.request.params
            for key, value in params.iteritems():
                blob_key = None
                # If we're dealing with a post from the blob store upload url,
                # get the blob key from the already stored blob.
                if isinstance(value, cgi.FieldStorage) and 'blob-key' in value.type_options:
                    info = blobstore.parse_blob_info(value)
                    blob_key = info.key()
                # Otherwise if we're dealing with our own base64 encoded data
                # decode it, save a blob and use its key.
                elif value and key in self._upload_files:
                    mime_type = self._upload_files.get(key)
                    data = base64.urlsafe_b64decode(encode_to_utf8(value))
                    blob_key = self._write_file(mime_type, data)
                # Either way, if we have a blob key, add it to self._uploads
                # and, if it's an image then set the corresponding `serving_url`.
                if blob_key is not None:
                    mime_type = self._upload_files.get(key)
                    if mime_type == 'image/jpeg':
                        serving_key = '%s_serving_url' % key
                        serving_url = images.get_serving_url(blob_key)
                        self._uploads[serving_key] = serving_url
                    self._uploads[key] = blob_key
        return self._uploads
        
    
    def _get_attrs(self):
        """ Get the attributes to update the context with from the 
        """
        
        attrs = {}
        error = u''
        
        params = self.request.params
        uploads = self._get_uploads()
        
        attrs['title'] = params.get('title')
        attrs['description'] = params.get('description')
        attrs['url'] = params.get('url', None)
        try:
            model.Design.url.validate(attrs['url'])
        except datastore_errors.BadValueError:
            msg = self._(u'Web link is not a valid URL.')
            hint = self._(u'(If you don\'t have a web link, leave the field blank)')
            error = '%s %s' % (msg, hint)
        
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
                    # If they're an admin (and thus won't be moderated) make sure
                    # they have an avatar here.
                    if users.is_current_user_admin() and not user.avatar:
                        user.set_avatar()
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
            else:
                attrs['status'] = u'pending'
            
            country_code = self.country_code
            try:
                country = pytz.country_names[country_code.lower()]
            except KeyError:
                country = country_code
            attrs['country'] = country
            
            attrs.update(uploads)
        
        return attrs, error
        
    
    
    @auth.required
    def _add_edit_form(self, context=None):
        """ Return page containing an add or edit form.
          
          n.b.: pops the last part of the url, so `../designs/add` becomes
          `../designs` and `../designs/1/edit` becomes `../designs/1`.
          
        """
        
        target = context
        series = model.Series.get_all()
        
        parts = self.request.path.split('/')
        if parts[-1] == 'sketchup':
            parts = parts[:-2]
        else:
            parts = parts[:-1]
        path = '/'.join(parts)
        upload_url = blobstore.create_upload_url(path)
        
        return self.render(
            'add_edit_form.tmpl',
            target=target,
            series=series,
            upload_url=upload_url
        )
        
    
    def _view_page(self, context):
        """ Return page to display the design.
        """
        
        series = model.Series.get_all()
        return self.render(
            'design.tmpl', 
            target=context, 
            series=series,
            disqus_dev_mode=self._disqus_dev_mode
        )
        
    
    def get(self, id=None, is_edit=False):
        """ If a context is provided, display it.  Otherwise, display an add form.
        """
        
        context = self._get_context(id)
        
        if context is None:
            return self._add_edit_form()
        
        elif is_edit:
            self._ensure_edit_allowed(context)
            return self._add_edit_form(context)
        
        return self._view_page(context)
        
    
    
    @auth.required
    def post(self, id=None, is_edit=False):
        """ Create a new `Design`.  Redirect afterwards to return JSON data
          indicating success or failure.
        """
        
        # If an `id` is provided, it's actually a `PUT`.  (Should only ever
        # have an `id` present in a `POST` if its a redirect from the blob
        # store upload url).
        if id is not None:
            return self.put(id)
        
        # Get the new design's properties from the request.
        attrs, error = self._get_attrs()
        
        # If there wasn't a problem, then save the new design, if appropriate
        # sending a notification email to the user and moderator alike.
        if not error:
            try: 
                design = model.Design(**attrs)
                design.put()
            except db.Error, err:
                error = unicode(err)
            else:
                if not users.is_current_user_admin():
                    self._send_notification(design)
                
        # If there was an error redirect to return the error data.
        if error:
            return self._redirect_on(error=error)
        
        # Otherwise redirect to return the id of the new design.
        return self._redirect_on(id=design.key().id())
        
    
    
    @auth.required
    def put(self, id):
        """ Update an existing `Design`.  Redirect afterwards to return JSON data
          indicating success or failure.
        """
        
        # Make sure the model exists
        context = self._get_context(id)
        if context is None:
            raise HTTPNotFound
        
        # Make sure the current user is allowed to edit it.
        self._ensure_edit_allowed(context)
        
        # Get the properties from the request.
        attrs, error = self._get_attrs()
        
        # If there wasn't a problem, then update the existing design, if appropriate
        # sending a notification email to the user and moderator alike.
        design = context
        if not error:
            try: 
                for k, v in attrs.iteritems():
                    setattr(design, k, v)
                design.put()
            except db.Error, err:
                error = unicode(err)
            else:
                if not users.is_current_user_admin():
                    self._send_notification(design)
                
        # If there was an error redirect to return the error data.
        if error:
            return self._redirect_on(error=error)
        
        # Otherwise redirect to return the id of the updated design.
        return self._redirect_on(id=id)
        
    
    
    @auth.required
    def delete(self, id):
        """ Delete an existing `Design`.  Redirect afterwards to return JSON data
          indicating success or failure.
          
          n.b.: Doesn't actually remove the entity from the datastore, instead sets
          the status to 'deleted'.
          
        """
        
        # Make sure the model exists
        context = self._get_context(id)
        if context is None:
            raise HTTPNotFound
        
        # Make sure the current user is allowed to edit it.
        self._ensure_edit_allowed(context)
        
        # If the user provided the confirmation param, "delete" the design.
        error = None
        confirmed = self.request.params.get('confirmed', False)
        if not confirmed:
            error = self._(u'You must confirm the delete.')
        else:
            try: 
                context.deleted = True
                context.put()
            except db.Error, err:
                error = unicode(err)
        
        # If there was an error redirect to return the error data.
        if error:
            return self._redirect_on(error=error)
        
        # Otherwise redirect to return the id of the deleted design.
        return self._redirect_on(id=id)
        
    
    


class RedirectSuccess(RequestHandler):
    """
    """
    
    @auth.required
    def get(self, id):
        path = '/library/designs/%s' % id
        return {'success': path}
        
    
    

class RedirectError(RequestHandler):
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
        body = u'%s\n\n%s %s\n%s %s/library/designs/%s\n\n%s\n\n%s%s\n\n%s\nWikiHouse\n%s\n' % (
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
        query = model.Design.all().order('-m')
        query = query.filter("deleted =", False).filter("status =", u'pending')
        designs = query.fetch(99)
        return self.render('moderate.tmpl', designs=designs)
    
    


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
                if design and design.model_preview and not design.deleted:
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
        raise HTTPNotFound
        
    
    


