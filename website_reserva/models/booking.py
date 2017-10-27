# -*- coding: utf-8 -*-

import cStringIO
import contextlib
import datetime
import hashlib
import inspect
import logging
import math
import mimetypes
import unicodedata
import os
import re
import time
import urlparse

from PIL import Image
from sys import maxint
import werkzeug
import openerp
from openerp.osv import orm, osv, fields
from openerp.tools import html_escape as escape, ustr, image_resize_and_sharpen, image_save_for_web
from openerp.tools.safe_eval import safe_eval
from openerp.addons.web.http import request

logger = logging.getLogger(__name__)

class website(osv.osv):
    _inherit = "website"
    
    def _image_booking(self, cr, uid, model, id, field, response, max_width=maxint, max_height=maxint, cache=None, context=None):
        """ Fetches the requested field and ensures it does not go above
        (max_width, max_height), resizing it if necessary.

        Resizing is bypassed if the object provides a $field_big, which will
        be interpreted as a pre-resized version of the base field.

        If the record is not found or does not have the requested field,
        returns a placeholder image via :meth:`~._image_placeholder`.

        Sets and checks conditional response parameters:
        * :mailheader:`ETag` is always set (and checked)
        * :mailheader:`Last-Modified is set iif the record has a concurrency
          field (``__last_update``)

        The requested field is assumed to be base64-encoded image data in
        all cases.
        """
        
        Model = self.pool[model]
        id = int(id)
        ids = Model.search(cr, uid,
                           [('id', '=', id)], context=context)
        if not ids and 'website_published' in Model._fields:
            ids = Model.search(cr, openerp.SUPERUSER_ID,
                               [('id', '=', id)], context=context)
        if not ids:
            return self._image_placeholder(response)

        concurrency = '__last_update'
        [record] = Model.read(cr, openerp.SUPERUSER_ID, [id],
                              [concurrency, field],
                              context=context)
        if concurrency in record:
            server_format = openerp.tools.misc.DEFAULT_SERVER_DATETIME_FORMAT
            try:
                response.last_modified = datetime.datetime.strptime(
                    record[concurrency], server_format + '.%f')
            except ValueError:
                # just in case we have a timestamp without microseconds
                response.last_modified = datetime.datetime.strptime(
                    record[concurrency], server_format)

        # Field does not exist on model or field set to False
        if not record.get(field):
            # FIXME: maybe a field which does not exist should be a 404?
            return self._image_placeholder(response)

        response.set_etag(hashlib.sha1(record[field]).hexdigest())
        response.make_conditional(request.httprequest)

        if cache:
            response.cache_control.max_age = cache
            response.expires = int(time.time() + cache)

        # conditional request match
        if response.status_code == 304:
            return response

        data = record[field].decode('base64')
        image = Image.open(cStringIO.StringIO(data))
        response.mimetype = Image.MIME[image.format]

        filename = '%s_%s.%s' % (model.replace('.', '_'), id, str(image.format).lower())
        response.headers['Content-Disposition'] = 'inline; filename="%s"' % filename

        if (not max_width) and (not max_height):
            response.data = data
            return response

        w, h = image.size
        max_w = int(max_width) if max_width else maxint
        max_h = int(max_height) if max_height else maxint

        if w < max_w and h < max_h:
            response.data = data
        else:
            size = (max_w, max_h)
            img = image_resize_and_sharpen(image, size, preserve_aspect_ratio=True)
            image_save_for_web(img, response.stream, format=image.format)
            # invalidate content-length computed by make_conditional as
            # writing to response.stream does not do it (as of werkzeug 0.9.3)
            del response.headers['Content-Length']

        return response
        
 
    def image_url_booking(self, cr, uid, record, field, size=None, context=None):
        """Returns a local url that points to the image field of a given browse record."""
        model = record._name
        sudo_record = record.sudo()
        id = '%s_%s' % (record.id, hashlib.sha1(sudo_record.write_date or sudo_record.create_date or '').hexdigest()[0:7])
        size = '' if size is None else '/%s' % size
        return '/reserva/image/%s/%s/%s%s' % (model, id, field, size)
 
     
