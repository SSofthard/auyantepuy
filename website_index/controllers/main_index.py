# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.web.controllers import main
from openerp import http, SUPERUSER_ID
from openerp.addons.website.models.website import slug


class index(main.Home):
    @http.route('/', auth='public', website=True)
    def index(self):
        cr, uid, context = http.request.cr, http.request.uid, http.request.context
        return http.request.website.render('website_index.index', {
        })


    #~ @http.route(['/register'], type='http', auth='public', website=True)
    #~ def register(self,**kwargs):
        #~ data={}
        #~ cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        #~ register_obj = registry.get('res.users')
        #~ print kwargs['contact_name']
        #~ print kwargs['contact_email']
        #~ data ={
            #~ 'name':kwargs['contact_name'],
            #~ 'email': kwargs['contact_email'],
            #~ 'login': kwargs['contact_email'],
            #~ 'in_group_40': True,
            #~ 'sel_groups_5': False,
        #~ }
        #~ user_id = register_obj.create(cr, SUPERUSER_ID, data, context=context)
        #~ user_data=register_obj.browse(cr,SUPERUSER_ID,user_id)
        #~ partner_obj=registry.get('res.partner')
        #~ print user_data.partner_id.id
        #~ print user_data.partner_id.id
        #~ print user_data.partner_id.id
        #~ print user_data.partner_id.id
        #~ partner_return=partner_obj.write(cr,SUPERUSER_ID,user_data.partner_id.id,{'customer':True,
                                                                                  #~ 'phone':kwargs['phone'],
                                                                                  #~ 'country_id': 240,
                                                                                  #~ 'city':kwargs['contact_city'],
                                                                                  #~ 'street':kwargs['contact_calle'],
                                                                                    #~ })
#~ 
        #~ return http.request.website.render('website_index.mail_index',{ 
        #~ })



    @http.route('/reset_passwd/<login>', type='http', auth='public', website=True)
    def cambiar_passwd(self,**login):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        user_id=registry.get('res.users').reset_password(cr, SUPERUSER_ID, login['login'])
        return http.request.website.render('website_index.mail_reset_password',{
        })
    

