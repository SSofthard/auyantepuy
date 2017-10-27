# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp.osv import fields, osv
from openerp import netsvc
from datetime import datetime, date, time, timedelta
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import collections


class res_partner(osv.Model):
    _inherit= "res.partner"
    _columns= {
        'partner_id':fields.many2one('hotel.reservation','Contactos'),
    }

class hotel_reservation(osv.Model):
    _name = "hotel.reservation"
    _rec_name = "reservation_no"
    _description = "Reservation"
    _order = 'reservation_no desc'
    id_filter=[]
    
    def default_get(self, cr, uid, fields, context=None):
         if context is None:
             context = {}
         res = super(hotel_reservation, self).default_get(cr, uid, fields, context=context)
         if context:
             keys = context.keys()
             if 'date' in keys:
                 fecha,hora=context['date'].split(' ')
                 a,m,d=fecha.split('-')
                 checkout=date(int(a),int(m),int(d)+1)
                 checkout=checkout.strftime("%Y-%m-%d")
                 checkout=checkout+' '+hora
                 res.update({'checkin': context['date']})
             if 'room_id' in keys:
                 res.update({'reservation_line':[(0, 0, {'reserve': [(6, 0, [int(context['room_id'])])]})]})

         return res
    
    def duracion(self,cr,uid,checkin_date,checkout_date,context=None):
        duration_vals=self.onchange_dates(cr, uid, [], checkin_date=checkin_date, checkout_date=checkout_date, duration=False)
        duration = duration_vals.get('value', False) and duration_vals['value'].get('duration') or 0.0
        if duration==0:
            duration=1
        return duration 
    def sub_total(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        sudtotal_room=0
        sudtotal_serv=0
        dias=1
        records=self.browse(cr,uid,ids)
        for r in records:
            dias=self.duracion(cr,uid,r.checkin,r.checkout,context=context)
            for h in r.reservation_line:
                for lp in h.reserve: 
                    sudtotal_room=sudtotal_room+lp.list_price
            for s in r.service_recervation_line:
                sudtotal_serv=sudtotal_serv+(s.service_id.list_price*s.product_uom_qty)
            res[r.id]=(sudtotal_room+sudtotal_serv)*dias
        return res
    def verificar_pago(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        records=self.browse(cr,uid,ids)
        account_invoice_obj=self.pool.get('account.invoice')
        for r in records:
            if not r.state=='done':
                if r.acccount_invoice_id:
                    for account_invoice in account_invoice_obj.browse(cr,uid,[r.acccount_invoice_id]):
                        if account_invoice.state=='paid':
                            self.write(cr, uid, ids, {'state':'paid'},context=context)
                            res[r.id]=1
        return res
            
    def cuentas_iva(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        iva_room=0
        iva_serv=0
        dias=1
        cont=0
        records=self.browse(cr,uid,ids)
        for r in records:
            dias=self.duracion(cr,uid,r.checkin,r.checkout,context=context)
            for h in r.reservation_line:
                for lp in h.reserve: 
                    iva_room=iva_room+(lp.taxes_id.amount*lp.list_price)
            for s in r.service_recervation_line:
                    iva_serv=iva_serv+(s.service_id.taxes_id.amount*(s.product_uom_qty*s.service_id.list_price))
            res[r.id]=(iva_room+iva_serv)*dias
        return res
        
    def cuenta_total(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        total_room=0
        total_serv=0
        dias=1
        cont=0
        records=self.browse(cr,uid,ids)
        for r in records:
            dias=self.duracion(cr,uid,r.checkin,r.checkout,context=context)
            for h in r.reservation_line:
                for ct in h.reserve:
                    total_room=total_room+ct.costo_total
              
            for s in r.service_recervation_line:
                total_serv=total_serv+(s.service_id.costo_total*s.product_uom_qty)
            res[r.id]=(total_room+total_serv)*dias
        return res
        
    def dias_hospedaje(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        records=self.browse(cr,uid,ids)
        for r in records:
            res[r.id]=self.duracion(cr,uid,r.checkin,r.checkout,context=context)
        return res
    
    _columns = {
        'reservation_no': fields.char('Reservation No', size=64, readonly=True),
        'date_order':fields.datetime('Date Ordered', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'warehouse_id':fields.many2one('stock.warehouse', 'Hotel', readonly=True, required=True, states={'draft':[('readonly', False)]}),
        'partner_id':fields.many2one('res.partner', 'Guest Name', readonly=True, required=True, states={'draft':[('readonly', False)]}),
        'pricelist_id':fields.many2one('product.pricelist', 'Lista de precios', required=True, readonly=True, states={'draft':[('readonly', False)]}, help="Pricelist for current reservation. "),
        'partner_invoice_id':fields.many2one('res.partner', 'Invoice Address', readonly=True, states={'draft':[('readonly', False)]}, help="Invoice address for current reservation. "),
        'partner_order_id':fields.many2one('res.partner', 'Ordering Contact', readonly=True, states={'draft':[('readonly', False)]}, help="The name and address of the contact that requested the order or quotation."),
        'partner_shipping_id':fields.many2one('res.partner', 'Dirección de envío', readonly=True, states={'draft':[('readonly', False)]}, help="Delivery address for current reservation. "),
        'checkin': fields.datetime('Expected-Date-Arrival', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'checkout': fields.datetime('Expected-Date-Departure', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'adults':fields.integer('Adults', size=64, readonly=True, states={'draft':[('readonly', False)]}, help='List of adults there in guest list. '),
        'children':fields.integer('Children', size=64, readonly=True, states={'draft':[('readonly', False)]}, help='Number of children there in guest list. '),
        'reservation_line':fields.one2many('hotel_reservation.line', 'line_id', 'Reservation Line', help='Hotel room reservation details. '),
        'service_recervation_line':fields.one2many('hotel_reservation_service.line','serviline_id', 'Reservation Line', help='Hotel service reservation details. '),
        'child_ids':fields.one2many('res.partner','partner_id', 'Huespedes'),
        'state': fields.selection([('draft', 'Draft'), ('confirm', 'Confirm'),('invoiced', 'Invoiced'),('paid', 'Paid'), ('done', 'Culminado'), ('cancel', 'Cancel')], 'State', readonly=True),
        'dummy': fields.datetime('Dummy'),
        'sub_total':fields.function(sub_total,type='float',string='Sub Total'),
        'cuenta_iva':fields.function(cuentas_iva,type='float',string='IVA'),
        'cuenta_total':fields.function(cuenta_total,type='float',string='Total'),
        'acccount_invoice_id':fields.integer('Id de la factura',readonly=True,),
        'verificar_pago':fields.function(verificar_pago,string='Verificar Pago'),
        'fecha_salida': fields.datetime('Fecha de salida del cliente', readonly=True,),
        'dias_hospedaje':fields.function(dias_hospedaje,type='integer',string='Días de Hospedaje'),

    }
    _defaults = {
        'state': lambda *a: 'draft',
        'date_order': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'warehouse_id': 1,
    }
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def create(self,cr,uid,values,context=None):
        values.update({
            'reservation_no':self.pool.get('ir.sequence').get(cr,uid,'hotel.reservation')})
        return super(hotel_reservation,self).create(cr,uid,values,context=context)
        
        
    def on_change_checkin(self, cr, uid, ids, date_order, checkin_date=time.strftime('%Y-%m-%d %H:%M:%S'),checkout_date=time.strftime('%Y-%m-%d %H:%M:%S'), context=None):
        if date_order and checkin_date:
            if checkin_date < date_order:
                raise osv.except_osv(_('Advertencia'), _('la fecha de llegada debe ser mayor a la fecha actual.'))
        return {'value':{'dias_hospedaje':self.duracion(cr,uid,checkin_date,checkout_date,context=context)}}

    def on_change_checkout(self, cr, uid, ids, checkin_date=time.strftime('%Y-%m-%d %H:%M:%S'), checkout_date=time.strftime('%Y-%m-%d %H:%M:%S'), context=None):
        if not (checkout_date and checkin_date):
            return {'value':{}}
        if checkout_date < checkin_date:
            raise osv.except_osv(_('Advertencia'), _('La fecha de salida debe ser mayor a la fecha de llegada.'))
        delta = timedelta(days=1)
        addDays = datetime(*time.strptime(checkout_date, '%Y-%m-%d %H:%M:%S')[:5]) + delta
        val = {'value':{'dummy':addDays.strftime('%Y-%m-%d %H:%M:%S'),'dias_hospedaje':self.duracion(cr,uid,checkin_date,checkout_date,context=context)}}
        return val

    def onchange_partner_id(self, cr, uid, ids, partner_id):
        if not partner_id:
            return {'value':{'partner_invoice_id': False, 'partner_shipping_id':False, 'partner_order_id':False}}
        partner_obj = self.pool.get('res.partner')
        addr = partner_obj.address_get(cr, uid, [partner_id], ['delivery', 'invoice', 'contact'])
        pricelist = partner_obj.browse(cr, uid, partner_id).property_product_pricelist.id
        return {'value':{'partner_invoice_id': addr['invoice'], 'partner_order_id':addr['contact'], 'partner_shipping_id':addr['delivery'], 'pricelist_id': pricelist}}

    def cancel_reservation(self,cr,uid,ids,context=None):
        if self.browse(cr,uid,ids,context=context).state=='confirm':
            h_room_reservation_line_obj=self.pool.get('hotel.room.reservation.line')
            h_room_reservation_line_ids=h_room_reservation_line_obj.search(cr,uid,[('reservation_id','in',ids)])
            h_room_reservation_line_obj.write(cr, uid,
                                                        h_room_reservation_line_ids, 
                                                        {'state':'unassigned'})
            
        self.write(cr, uid, ids, {'state':'cancel'},context=context)
        return True
    def reservation_done(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'done','fecha_salida':datetime.now()},context=context)
        return True
    def draft_reservation(self,cr,uid,ids):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
       
    def confirmed_reservation(self,cr,uid,ids,context=None):
        hotel_room_reservation_line_vals=[]
        hotel_room_reservation_line_obj=self.pool.get('hotel.room.reservation.line')
        for reservation in self.browse(cr, uid, ids,context=context):
            for h in reservation.reservation_line:
                for room in h.reserve:
                    hotel_room_reservation_line_vals={
                                'room_id':room.id,
                                'check_in':reservation.checkin,
                                'check_out':reservation.checkout,
                                'state':'assigned',
                                'reservation_id':reservation.id
                                }
                    hotel_room_reservation_line_obj.create(cr, uid, hotel_room_reservation_line_vals, context=context)
        self.write(cr, uid, ids, {'state':'confirm'},context=context)
        #~ res=hotel_reservation.facturar_pagar(self, cr, uid, ids, context=None) 
        return True

    def imprimir_factura(self, cr, uid, ids, context=None):
        for reserva in self.browse(cr,uid,ids,context=context):
                acccount_invoice_id=reserva.acccount_invoice_id
        return self.pool['report'].get_action(cr, uid, [acccount_invoice_id], 'account.report_invoice', context=context)
        
    def facturar_pagar(self, cr, uid, ids, context=None):
        account_invoice_obj=self.pool.get('account.invoice')
        account_line_obj=self.pool.get('account.invoice.line')
        account_obj=self.pool.get('account.account')
        #~ Realizamos un search para obtener los ids con las condiciones dadas dentro del mismo
        account_ids=account_obj.search(cr, 
                                        uid, 
                                        [('code', '=',1122001),
                                         ('name','=','CUENTAS POR COBRAR CLIENTES'),
                                        ])
        #~ a los ids del search le hacemos un browse para obtener los datos especificos de esa busqueda
        account_data=account_obj.browse(cr,uid,account_ids, context=context)
        # Realizamos un search para obtener los ids con las condiciones dadas dentro del mismo
        account_line_ids=account_obj.search(cr, 
                                        uid, 
                                        [('code', '=',5111002),
                                         ('name','=','VENTAS NACIONALES AL DETAL'),
                                        ])
        # Realizamos un browse para obtener los valores del search antes realizado
        account_line_data=account_obj.browse(cr,uid,account_line_ids, context=context)
        for reservation in self.browse(cr, uid, ids, context=context):
            account_invoice_vals=[]
            account_line_vals=[]
            checkin_date, checkout_date = reservation['checkin'], reservation['checkout']
            if not checkin_date < checkout_date:
                raise osv.except_osv(_('Error'), _('Fechas Invalidas'))
            duration_vals=self.onchange_dates(cr, uid, [], checkin_date=checkin_date, checkout_date=checkout_date, duration=False)
            duration = duration_vals.get('value', False) and duration_vals['value'].get('duration') or 0.0
            for line in reservation.reservation_line:
                for r in line.reserve:
                    tax= [t.id for t in r.taxes_id]
                    #~ Aqui Adicionamos la variable que contendra los valores de account invoiced line por cada reserva
                    account_line_vals.append(list((0,False,{
                        'uos_id': r.product_id and r.product_id.id, 
                        'account_id': account_line_data.id, 
                        'price_unit': r['lst_price'], 
                        'quantity': duration,
                        'invoice_line_tax_id': [[6, False, [tax[0]]]], 
                        'product_id': r.product_id and r.product_id.id, 
                        'name': r.name, 
                        'account_analytic_id': False, 
                        })))
                    
            for line in reservation.service_recervation_line:
                for r in line.service_id:
                    tax= [t.id for t in r.taxes_id]
                    #~ Aqui Adicionamos la variable que contendra los valores de account invoiced line por cada servicio
                    account_line_vals.append(list((0,False,{
                        'uos_id': r.service_id.product_variant_ids and r.service_id.product_variant_ids.id, 
                        'account_id': account_line_data.id, 
                        'price_unit': r['lst_price'], 
                        'quantity': line.product_uom_qty*duration,
                        'invoice_line_tax_id': [[6, False, [tax[0]]]], 
                        'product_id': r.service_id.product_variant_ids and r.service_id.product_variant_ids.id, 
                        'name': r.name, 
                        'account_analytic_id': False, 
                        })))
             #~ Aqui llenamos una variable que contendra los valores de account invoiced
            account_invoice_vals={
                'name':reservation['reservation_no'],
                'reference':reservation['reservation_no'],
                'origin':reservation['reservation_no'],
                'account_id':account_data.id,
                'partner_id':reservation.partner_id.id,
                'date_due':date.today(),
                'user_id':uid,
                'amount_total':reservation['cuenta_total'],
                'amount_untaxed':reservation['cuenta_total'],
                'isawning':True,
                }
            # Aqui actualizamos los valores que trae esta variable y le pasamos en el atributo invoice_line los valores adicionados 
            account_invoice_vals.update({'invoice_line': account_line_vals})
            # Mediante esta variable que inicializamos al comienzo llamos al metodo para crear la factura
            acccount_invoice_id=account_invoice_obj.create(cr, uid, account_invoice_vals, context=context)
            #~ con esto manipulo el workflow de account invoice para validar la factura 
            account_invoice_obj.signal_workflow(cr, uid, [acccount_invoice_id], 'invoice_open')
            #~ con esto pulso el boton de registrar pago y el por defecto me devuelve la vista de cancelar la 
            #~ factura
            vista_pago=account_invoice_obj.invoice_pay_customer(cr,uid,[acccount_invoice_id])
            self.write(cr, uid, ids, {'state':'invoiced','acccount_invoice_id':acccount_invoice_id},context=context)
            return vista_pago
        

    def onchange_dates(self, cr, uid, ids, checkin_date=False, checkout_date=False, duration=False):
        # This mathod gives the duration between check in checkout if customer will leave only for some hour it would be considers as
        # a whole day. If customer will checkin checkout for more or equal hours , which configured in company as additional hours than
        # it would be consider as full day
        
        value = {}
        company_obj = self.pool.get('res.company')
        configured_addition_hours = 0
        company_ids = company_obj.search(cr, uid, [])
        if company_ids:
            company = company_obj.browse(cr, uid, company_ids[0])
            configured_addition_hours = company.additional_hours
        if not duration:
            duration = 0
            if checkin_date and checkout_date:
                chkin_dt = datetime.strptime(checkin_date, '%Y-%m-%d %H:%M:%S')
                chkout_dt = datetime.strptime(checkout_date, '%Y-%m-%d %H:%M:%S')
                dur = chkout_dt - chkin_dt
                duration = dur.days
                if configured_addition_hours > 0:
                    additional_hours = abs((dur.seconds / 60) / 60)
                    if additional_hours >= configured_addition_hours:
                        duration += 1
            value.update({'value':{'duration':duration}})
        else:
            if checkin_date:
                chkin_dt = datetime.strptime(checkin_date, '%Y-%m-%d %H:%M:%S')
                chkout_dt = chkin_dt + timedelta(days=duration)
                checkout_date = datetime.strftime(chkout_dt, '%Y-%m-%d %H:%M:%S')
                value.update({'value':{'checkout_date':checkout_date}})
        return value
    
    
    def pagar_reserva(self, cr, uid, ids, context=None):
        account_invoice_obj=self.pool.get('account.invoice')
        for reservation in self.browse(cr, uid, ids, context=context):
                for account_invoice in account_invoice_obj.browse(cr,uid,[reservation.acccount_invoice_id]):
                    if not account_invoice.state=='paid':
                        vista_pago=account_invoice_obj.invoice_pay_customer(cr,uid,[reservation.acccount_invoice_id]) 
                        return vista_pago
        return True
    
    def on_change_filter(self, cr, uid, ids, reservation_line, context=None):
        hotel_reservation.id_filter=[]
        list_id=[]
        for h in reservation_line:
            for ct in h:
                try: iterator = iter(ct) 
                except TypeError:
                    a=1
                else:
                    if 'reserve' in ct:
                        for l in ct['reserve']:
                            list_id.extend(l[2])
                            hotel_reservation.id_filter=list_id
        return True
            

class hotel_reservation_line(osv.Model):
    _name = "hotel_reservation.line"
    _description = "Reservation Line"
    _columns = {
         'name':fields.char('Name', size=64),
         'line_id':fields.many2one('hotel.reservation'),
         'reserve':fields.many2many('hotel.room', 'hotel_reservation_line_room_rel', 'room_id', 'hotel_reservation_line_id', domain="[('isroom','=',True),('categ_id','=',categ_id)]"),
         'categ_id': fields.many2one('product.category', 'Room Type', domain="[('isroomtype','=',True)]", change_default=True),
        }

    def on_change_categ(self, cr, uid, ids, categ_ids, checkin, checkout, context=None):
        hotel_room_obj = self.pool.get('hotel.room')
        hotel_room_ids = hotel_room_obj.search(cr, uid, [('categ_id', '=', categ_ids)], context=context)
        assigned = False
        room_ids = []
        if not checkin:
            raise osv.except_osv(_('No se encuentra definida una fecha de llegada'), _('Antes de escoger una habitación\nDebe seleccionar una fecha de llegada en el formulario de reservación.'))
        for room in hotel_room_obj.browse(cr, uid, hotel_room_ids, context=context):
            assigned = False
            for line in room.room_reservation_line_ids:
                if line.check_in == checkin and line.check_out == checkout:
                    assigned = True
            if not assigned:
                room_ids.append(room.id)
        if type(categ_ids) == int:
            room_idt=tuple(room_ids)
            if room_ids:
                #~ 
                cr.execute("select hotel_reservation_line_id from hotel_reservation as hr " \
                    "inner join hotel_reservation_line as hrl on hrl.line_id = hr.id " \
                    "inner join hotel_reservation_line_room_rel as hrlrr on hrlrr.room_id = hrl.id " \
                    "where (checkin,checkout) overlaps ( timestamp %s , timestamp %s ) " \
                    "and hrlrr.hotel_reservation_line_id  in %s and categ_id=cast(%s as integer) " \
                    "and hr.state<>'cancel'"\
                    ,(str(checkin),str(checkout),room_idt,categ_ids)
                          )
                for row in cr.fetchall():
                    row=set(row)
                    room_ids=set(room_ids)
                    room_ids=room_ids-row
    
        domain = {'reserve': [('id', 'in', list(room_ids)),('id', 'not in', list(hotel_reservation.id_filter))]}
        
        
        return {'domain': domain}
        
    def consult_booking(self, cr, uid, ids, checkin, checkout, booking_adult, booking_child, context=None):
        hotel_room_obj = self.pool.get('hotel.room')
        hotel_room_ids = hotel_room_obj.search(cr, uid, [('max_adult', '>=', booking_adult), ('max_child', '>=', booking_child), ('website_published', '=', True)], context=context)
        assigned = False
        room_ids = []
        if not checkin:
            raise osv.except_osv(_('No se encuentra definida una fecha de llegada!'), _('Antes de escoger una habitación\nDebe seleccionar una fecha de llegada en el formulario de reservación'))
        for room in hotel_room_obj.browse(cr, uid, hotel_room_ids, context=context):
            assigned = False
            for line in room.room_reservation_line_ids:
                if line.check_in == checkin and line.check_out == checkout:
                    assigned = True
            if not assigned:
                room_ids.append(room.id)
        
        room_idt=tuple(room_ids)
        if room_ids:
            cr.execute("select hotel_reservation_line_id from hotel_reservation as hr " \
                "inner join hotel_reservation_line as hrl on hrl.line_id = hr.id " \
                "inner join hotel_reservation_line_room_rel as hrlrr on hrlrr.room_id = hrl.id " \
                "where (checkin,checkout) overlaps ( timestamp %s , timestamp %s ) " \
                "and hrlrr.hotel_reservation_line_id  in %s and  hr.state<>'cancel'"\
                ,(str(checkin),str(checkout),room_idt)
                      )
            for row in cr.fetchall():
                row=set(row)
                room_ids=set(room_ids)
                room_ids=room_ids-row
    
        
        return list(room_ids)
        

class hotel_room_reservation_line(osv.Model):
    _name = 'hotel.room.reservation.line'
    _description = 'Hotel Room Reservation'
    _rec_name = 'room_id'
    _columns = {
        'room_id': fields.many2one('hotel.room', 'Room id'),
        'check_in':fields.datetime('Check In Date', required=True),
        'check_out': fields.datetime('Check Out Date', required=True),
        'state': fields.selection([('assigned', 'Assigned'), ('unassigned', 'Unassigned')], 'Room Status'),
        'reservation_id': fields.many2one('hotel.reservation', 'Reservation'),
    }

hotel_room_reservation_line()


class hotel_room(osv.Model):
    _inherit = 'hotel.room'
    _description = 'Hotel Room'
    _columns = {
        'room_reservation_line_ids': fields.one2many('hotel.room.reservation.line', 'room_id', 'Room Reservation Line'),
    }


    #~ def cron_room_line(self, cr, uid, context=None):
        #~ reservation_line_obj = self.pool.get('hotel.room.reservation.line')
        #~ now = datetime.now()
        #~ curr_date = now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        #~ room_ids = self.search(cr, uid, [], context=context)
        #~ for room in self.browse(cr, uid, room_ids, context=context):
            #~ status = {}
            #~ reservation_line_ids = [reservation_line.id for reservation_line in room.room_reservation_line_ids]
            #~ reservation_line_ids = reservation_line_obj.search(cr, uid, [('id', 'in', reservation_line_ids), ('check_in', '<=', curr_date), ('check_out', '>=', curr_date)], context=context)
            #~ if reservation_line_ids:
                #~ status = {'status': 'occupied'}
            #~ else:
                #~ status = {'status': 'available'}
            #~ self.write(cr, uid, [room.id], status, context=context)
        #~ return True

class room_reservation_summary(osv.Model):
     _name = 'room.reservation.summary'
     _description = 'Room reservation summary'
     _columns = {
         'date_from':fields.datetime('Date From'),
         'date_to':fields.datetime('Date To'),
         'summary_header':fields.text('Summary Header'),
         'room_summary':fields.text('Room Summary'),
     }
 
     def room_reservation(self, cr, uid, ids, context=None):
         mod_obj = self.pool.get('ir.model.data')
         if context is None:
             context = {}
         model_data_ids = mod_obj.search(cr, uid, [('model', '=', 'ir.ui.view'), ('name', '=', 'view_hotel_reservation_form')], context=context)
         resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
         return {
             'name': _('Reconcile Write-Off'),
             'context': context,
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'hotel.reservation',
             'views': [(resource_id, 'form')],
             'type': 'ir.actions.act_window',
             'target': 'new',
         }
 
     def get_room_summary(self, cr, uid, ids, date_from, date_to, context=None):
 
         res = {}
         all_detail = []
         room_obj = self.pool.get('hotel.room')
         reservation_line_obj = self.pool.get('hotel.room.reservation.line')
         date_range_list = []
         main_header = []
         summary_header_list = ['Habitaciones']
         if date_from and date_to:
             if date_from > date_to:
                 raise osv.except_osv(_('Error!'), _('El campo de fecha "Desde" no debe ser mayor al campo de fecha "Hasta"'))
             d_frm_obj = datetime.strptime(date_from, DEFAULT_SERVER_DATETIME_FORMAT)
             d_to_obj = datetime.strptime(date_to, DEFAULT_SERVER_DATETIME_FORMAT)
             temp_date = d_frm_obj
             while(temp_date <= d_to_obj):
                 val = ''
                 val = str(temp_date.strftime("%a")) + ' ' + str(temp_date.strftime("%b")) + ' ' + str(temp_date.strftime("%d"))
                 summary_header_list.append(val)
                 date_range_list.append(temp_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
                 temp_date = temp_date + timedelta(days=1)
             all_detail.append(summary_header_list)
             room_ids = room_obj.search(cr, uid, [], context=context)
             all_room_detail = []
             for room in room_obj.browse(cr, uid, room_ids, context=context):
                 room_detail = {}
                 room_list_stats = []
                 room_detail.update({'name':room.name or ''})
                 if not room.room_reservation_line_ids:
                     for chk_date in date_range_list:
                         room_list_stats.append({'state':'Disponible', 'date':chk_date, 'room_id':room.id})
                 else:
                     for chk_date in date_range_list:
                         for room_res_line in room.room_reservation_line_ids:
                             reservation_line_ids = [i.id for i in room.room_reservation_line_ids]
                             #~ agregue la condicion del estado pra cuando cancelan la recervation
                             reservation_line_ids = reservation_line_obj.search(cr, uid, [
                                                                                        ('id', 'in', reservation_line_ids),
                                                                                        ('check_in', '<=', chk_date), 
                                                                                        ('check_out', '>=', chk_date),
                                                                                        ('state','=','assigned')
                                                                                        ])
                             if reservation_line_ids:
                                 room_list_stats.append({'state':'Reservado', 'date':chk_date, 'room_id':room.id})
                                 break
                             else:
                                 room_list_stats.append({'state':'Disponible', 'date':chk_date, 'room_id':room.id})
                                 break
                 room_detail.update({'value':room_list_stats})
                 all_room_detail.append(room_detail)
             main_header.append({'header':summary_header_list})
             res.update({'value':{'summary_header': str(main_header), 'room_summary':str(all_room_detail)}})
         return res
 




class hotel_service_line(osv.Model):
    _name = 'hotel_reservation_service.line'
    _description = "Reservation Service Line"
    
    def limpiar_selector(self, cr, uid, ids,context=None):
        res={}
        res = {
        'service_id':'',
                }
        return {'value':res}
    
    _columns = {
        'name':fields.char('Name', size=64),
        'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        'categ_id': fields.many2one('product.category', 'Tipo de servicios', domain="[('isservicetype','=',True)]", change_default=True),
        'serviline_id':fields.many2one('hotel.reservation'),
        'service_id':fields.many2one('hotel.services',"Services"),
        #~ 'service':fields.many2many('hotel.services', 'hotel_reservation_line_services_rel', 'service_id', 'hotel_reservation_line_id', domain="[('categ_id','=',categ_id)]"),
        }
    _defaults = {
        'product_uom_qty':1
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
