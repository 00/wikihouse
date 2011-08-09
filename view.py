#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ``RequestHandler``s.
"""

from __future__ import with_statement

import base64
import cgi
import logging

from pytz.gae import pytz

from google.appengine.api import files, mail, users
from google.appengine.ext import blobstore, db

from weblayer import RequestHandler
from weblayer.utils import encode_to_utf8, unicode_urlencode

import auth
import model

class Index(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('index.tmpl')
        
    
    


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
        
    
    


class Library(RequestHandler):
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
        
        # Get either the most recent 9 `Design`s or the `Design`s in the
        # target `Series`.
        if target is None:
            query = model.Design.all().filter("status =", u'approved')
            designs = query.order('-m').fetch(9)
        else:
            designs = target.designs
        
        # Render the template.
        return self.render(
            'library.tmpl', 
            series=series, 
            target=target, 
            designs=designs
        )
        
    
    


class AddDesign(RequestHandler):
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
            f.write(data)
        
        # Finalize the file. Do this before attempting to read it.
        files.finalize(file_name)
        
        # Get the file's blob key
        return files.blobstore.get_blob_key(file_name)
        
    
    def _get_uploads(self):
        """ Lazy decode and store file uploads.
        """
        
        if self._uploads is None:
            self._uploads = {}
            params = self.request.params
            for key, value in params.iteritems():
                if value and key in self._upload_files:
                    mime_type = self._upload_files.get(key)
                    data = base64.urlsafe_b64decode(encode_to_utf8(value))
                    blob_key = self._write_file(mime_type, data)
                    self._uploads[key] = blob_key
        return self._uploads
        
    
    
    def notify(self, design):
        """ Notify the moderators.
        """
        
        url = self.request.host_url
        user = users.get_current_user()
        
        sender = user.email()
        subject = u'New design submitted to WikiHouse.'
        body = u'Please moderate the submission:\n\n%s/moderate\n' % url
        
        recipients = self.settings['moderation_notification_email_addresses']
        for item in recipients:
            message = mail.EmailMessage(
                to=item,
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
        
        attrs['verification'] = params.get('verification')
        attrs['notes'] = params.get('notes')
        attrs['sketchup_version'] = params.get('sketchup_version')
        
        country_code = self.request.headers.get('X-AppEngine-Country', 'GB')
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
    
    @auth.admin
    def post(self):
        params = self.request.params
        action = params.get('action')
        design = model.Design.get_by_id(int(params.get('id')))
        if action == 'Approve':
            design.status = u'approved'
        elif action == 'Reject':
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
        series = model.Series.get_all()
        return self.render(
            'design.tmpl', 
            target=target, 
            series=series,
            dev=self.settings['dev']
        )
        
    
    


class NotFound(RequestHandler):
    """
    """
    
    def get(self):
        return self.render('errors/404.tmpl')
        
    
    


