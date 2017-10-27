# -*- coding: utf-8 -*-

from openerp import http
from openerp.addons.web.controllers import main
from openerp.osv import orm, osv, fields


class reserva_paquete(osv.Model):
    _name = "reserva_paquete"
    _rec_name = "contact_name"
    
    _columns = {
        'contact_name': fields.text('Nombre Completo', size=100, required=True, select=True),
        'contact_phone': fields.integer('Teléfono', size=15, required=True, select=True),
        'contact_email': fields.char('Correo electrónico', size=35, required=True, select=True),
    }
    
