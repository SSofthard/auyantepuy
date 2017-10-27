# -*- coding: utf-8 -*-
import base64
import werkzeug
import werkzeug.urls
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request, STATIC_CACHE
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers.main import login_redirect
from datetime import datetime,date
import time 
import logging

logger = logging.getLogger(__name__)

PPG = 20 # Products Per Page
PPR = 4  # Products Per Row

class reserva(http.Controller):
    
    def generate_google_map_url(self, street, city, city_zip, country_name):
        url = "http://maps.googleapis.com/maps/api/staticmap?center=%s&sensor=false&zoom=8&size=298x298" % werkzeug.url_quote_plus(
            '%s, %s %s, %s' % (street, city, city_zip, country_name)
        )
        return url
    
    def placeholder(self, response):
        return request.registry['website']._image_placeholder(response)
    
    @http.route([
        '/reserva/image',
        '/reserva/image/<model>/<id>/<field>',
        '/reserva/image/<model>/<id>/<field>/<int:max_width>x<int:max_height>'
        ], auth="public", website=True)
        
    def website_image(self, model, id, field, max_width=None, max_height=None):
        """ Fetches the requested field and ensures it does not go above
        (max_width, max_height), resizing it if necessary.

        If the record is not found or does not have the requested field,
        returns a placeholder image via :meth:`~.placeholder`.

        Sets and checks conditional response parameters:
        * :mailheader:`ETag` is always set (and checked)
        * :mailheader:`Last-Modified is set iif the record has a concurrency
          field (``__last_update``)

        The requested field is assumed to be base64-encoded image data in
        all cases.
        """
        try:
            idsha = id.split('_')
            id = idsha[0]
            response = werkzeug.wrappers.Response()
            return request.registry['website']._image_booking(
                request.cr, request.uid, model, id, field, response, max_width, max_height,
                cache=STATIC_CACHE if len(idsha) > 1 else None)
        except Exception:
            logger.exception("Cannot render image field %r of record %s[%s] at size(%s,%s)",
                             field, model, id, max_width, max_height)
            response = werkzeug.wrappers.Response()
            return self.placeholder(response)
            
    
    @http.route(['/reserva', '/reserva/page/<int:page>'], type='http', auth='public', website=True)
    def index(self, **kwargs):
        cr, uid, context = http.request.cr, http.request.uid, http.request.context
        values = {
        'valid_date':"",
        'hotel_data':[],
        'tent_data':[],
        'awning_data':[],
        'uid':uid
        }
        for field in ['description', 'partner_name', 'phone', 'contact_name', 'contact_apellido', 'email_from', 'name']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return http.request.website.render('website_reserva.reserva', values)
    

    def create_lead(self, request, values, kwargs):
        """ Allow to be overrided """
        cr, context = request.cr, request.context
        return request.registry['crm.lead'].create(cr, SUPERUSER_ID, values, context=dict(context, mail_create_nosubscribe=True))

    def preRenderThanks(self, values, kwargs):
        """ Allow to be overrided """
        company = request.website.company_id
        return {
            'google_map_url': self.generate_google_map_url(company.street, company.city, company.zip, company.country_id and company.country_id.name_get()[0][1] or ''),
            '_values': values,
            '_kwargs': kwargs,
        }

    def get_booking_response(self, values, kwargs):
        #~ values = self.preRenderThanks(values, kwargs)
        return request.website.render(kwargs.get("view_callback", "website_reserva.reserva"), values)
        
    @http.route(['/consulta/reserva'], type='http', auth="public", website=True)
    def consulta_reserva(self, **kwargs):
        registry = http.request.registry
        cr, uid, context = http.request.cr, http.request.uid, http.request.context
        #~ pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
        _TECHNICAL = ['show_info', 'view_from', 'view_callback']  # Only use for behavior, don't stock it
        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id', 'active']  # Allow in description
        _REQUIRED = ['name', 'contact_name', 'checkin','checkout']  # Could be improved including required from model
        booking_adult=int(kwargs['reserva_adultos'])
        booking_child=int(kwargs['reserva_ninios'])
        times=' 17:00:00'
        msj_value=''
        m,d,a=kwargs['reserva_checkin'].split('/')
        chekin_in=date(int(a),int(m),int(d))
        m,d,a=kwargs['reserva_checkout'].split('/')
        cheKout_out=date(int(a),int(m),int(d))
        valid_date=""
        destino={'hotel':False,'toldo':False,'carpa':False}
        #~ if cheKout_out < chekin_in or chekin_in < date.today():
        if cheKout_out < chekin_in :
            valid_date="Las fechas indicadas son incorrectas, por favor verifique"
        else:    
            if kwargs['reserva_destino']=='Destino >':
                destino['hotel']=True
                destino['toldo']=True
                destino['carpa']=True
            else:
                if kwargs['reserva_destino']=='Hotel Arawak':
                    destino['hotel']=True
                else:
                    if kwargs['reserva_destino']=='Isla Tortugas Toldos':
                        destino['toldo']=True
                    else:
                        if kwargs['reserva_destino']=='Isla Tortugas Carpas':
                            destino['carpa']=True
        
        #~ checkin=chekin_in.strftime("%d-%m-%Y")
        #~ checkout=cheKout_out.strftime("%d-%m-%Y")
        checkin=chekin_in.strftime("%Y-%m-%d")
        checkout=cheKout_out.strftime("%Y-%m-%d")
        checkin=checkin+times
        checkout=checkout+times
        post_file = []  # List of file to add to ir_attachment once we have the ID
        post_description = []  # Info to add after the message
        
        
       
       
        #~ values['medium_id']  = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID, 'crm.crm_medium_website')
        #~ values['section_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID, 'website.salesteam_website_sales')
        
        tent_data=[]
        tent_product={}
        awning_data=[]
        awning_product={}
        hotel_data=[]
        product={}
        categ_cant={}
       
        if destino['hotel']:
            hotel_reservation_line_obj=request.registry['hotel_reservation.line']
            hotel_room_ids=hotel_reservation_line_obj.consult_booking(cr, SUPERUSER_ID,[], checkin, checkout, booking_adult, booking_child)
            hotel_hotel_room_obj=request.registry['hotel.room']
            hotel_room_data=hotel_hotel_room_obj.browse(cr,SUPERUSER_ID,hotel_room_ids)
            
            categ_ids=[]
            for i in hotel_room_data:
                if i.categ_id not in categ_ids:
                    categ_ids.append(i.categ_id)
                    categ_cant[i.categ_id.name]=1
                    hotel_data.append(i)
                    print i.product_id
                    product[i.categ_id.id]=i.product_id
                else:
                    categ_cant[i.categ_id.name]+=categ_cant[i.categ_id.name]
                
                
        if destino['toldo']:
            awning_reservation_line_obj=request.registry['awning_reservation.line']
            awning_room_ids=awning_reservation_line_obj.consult_booking(cr, SUPERUSER_ID,[], checkin, checkout, booking_adult, booking_child)
            awning_awning_room_obj=request.registry['toldo.awning']
            toldo_awning_data=awning_awning_room_obj.browse(cr,SUPERUSER_ID,awning_room_ids)
            
            categ_ids=[]
            for i in toldo_awning_data:
                if i.categ_id not in categ_ids:
                    categ_ids.append(i.categ_id)
                    categ_cant[i.categ_id.name]=1
                    awning_data.append(i)
                    awning_product[i.categ_id.id]=i.product_id
                else:
                    categ_cant[i.categ_id.name]+=categ_cant[i.categ_id.name]
                
        
        if destino['carpa']:
            tent_reservation_line_obj=request.registry['reservation_tent_line']
            tent_room_ids=tent_reservation_line_obj.consult_booking(cr, SUPERUSER_ID,[], checkin, checkout, booking_adult, booking_child)
            tent_tent_room_obj=request.registry['tent.tent']
            carpa_tent_data=tent_tent_room_obj.browse(cr,SUPERUSER_ID,tent_room_ids)
            
            categ_ids=[]
            for i in carpa_tent_data:
                if i.categ_id not in categ_ids:
                    categ_ids.append(i.categ_id)
                    categ_cant[i.categ_id.name]=1
                    tent_data.append(i)
                    print i.product_id
                    tent_product[i.categ_id.id]=i.product_id
                else:
                    categ_cant[i.categ_id.name]+=categ_cant[i.categ_id.name]
        
        if not hotel_data and not awning_data and not tent_data:       
            msj_value="No hay disponibilidad, por favor intente con otra fecha..."
            
        values = {
        'valid_date':valid_date,
        'uid':uid,
        'hotel_data':hotel_data,
        'awning_data':awning_data,
        'tent_data':tent_data,
        'categ_cant':categ_cant,
        'product':product,
        'awning_product':awning_product,
        'tent_product':tent_product,
        'msj_value':msj_value,
        #~ 'booking_obj':request.registry['booking']
        }
        return self.get_booking_response(values, kwargs)
        
