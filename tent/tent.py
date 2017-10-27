# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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


class product_category(osv.Model):
    _inherit = "product.category"
    _columns = {
        'istenttype':fields.boolean('Is Tent Type'),
        'istentservicetype':fields.boolean('Is Tent Service Type'),
    }

class product_product(osv.Model):
    _inherit = "product.product"
    _columns = {
        'istent':fields.boolean('Is Tent'),
        'iscategid':fields.boolean('Is categ id'),
        'istentservice':fields.boolean('Is Tent Service id'),
    }
    
class tent_type(osv.Model):
    _name = "tent.type"
    _inherits = {'product.category': 'cat_id'}
    _description = "Tipos de carpa"
    _columns = {
       'cat_id':fields.many2one('product.category', 'category', required=True, select=True, ondelete='cascade'),
    }
    _defaults = {
        'istenttype': 1,
        'categ_id': 'none',        
    }
    
class tent_tent(osv.Model):
    _name = 'tent.tent'
    _inherits = {'product.template': 'product_id'}
    _description = 'Tent'

    def costos_total(self, cursor, user, ids, name, arg, context=None):
		res = {}
		precision = self.pool.get('decimal.precision').precision_get(cursor, user, 'Account')
		for tent in self.browse(cursor, user, ids, context=context):
			res[tent.id] = round((tent.list_price+(tent.list_price*tent.taxes_id.amount)),precision)
		return res

    _columns = {
        'costo_total': fields.function(costos_total, string='Costo total', type='float'),
        'product_id': fields.many2one('product.template','product_id', required=True, ondelete='cascade'),
        'max_adult':fields.integer('Max Adultos'),
        'max_child':fields.integer('Max Niños'),
        'status':fields.selection([('disponible', 'Disponible'), ('ocupado', 'Ocupado')], 'Status'),
    }

    _defaults = {
        'istent': 1,
        'rental': 1,
        'status': 'disponible',
        'categ_id': '',
        'max_adult':2,
        'website_published':1,
    }

    def set_tent_status_occupied(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'status': 'ocupado'}, context=context)

    def set_tent_status_available(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'status': 'disponible'}, context=context)  
        
class tent_service_line(osv.Model):

    def copy(self, cr, uid, id, default=None, context=None):
        line_id = self.browse(cr, uid, id).service_line_id.id
        return self.pool.get('sale.order.line').copy(cr, uid, line_id, default=None, context=context)

    _name = 'tent.service.line'
    _description = 'Tent Service line'
    _inherits = {'sale.order.line':'service_line_id'}
    _columns = {
        'service_line_id': fields.many2one('sale.order.line', 'Service Line', required=True, ondelete='cascade'),
    }

    def unlink(self, cr, uid, ids, context=None):
        sale_line_obj = self.pool.get('sale.order.line')
        for line in self.browse(cr, uid, ids, context=context):
            if line.service_line_id:
                sale_line_obj.unlink(cr, uid, [line.service_line_id.id], context=context)
        return super(tent_service_line, self).unlink(cr, uid, ids, context=None)

    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):
        return self.product_id_change(cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=partner_id,
            lang=False, update_tax=True, date_order=False)

    def on_change_checkout(self, cr, uid, ids, checkin_date=None, checkout_date=None, context=None):
        if not checkin_date:
            checkin_date = time.strftime('%Y-%m-%d %H:%M:%S')
        if not checkout_date:
            checkout_date = time.strftime('%Y-%m-%d %H:%M:%S')
        qty = 1
        if checkout_date < checkin_date:
            raise osv.except_osv(_('Error !'), _('Checkout must be greater or equal checkin date'))
        if checkin_date:
            diffDate = datetime.datetime(*time.strptime(checkout_date, '%Y-%m-%d %H:%M:%S')[:5]) - datetime.datetime(*time.strptime(checkin_date, '%Y-%m-%d %H:%M:%S')[:5])
            qty = diffDate.days
        return {'value':{'product_uom_qty':qty}}

    def copy_data(self, cr, uid, id, default=None, context=None):
        line_id = self.browse(cr, uid, id).service_line_id.id
        return self.pool.get('sale.order.line').copy_data(cr, uid, line_id, default=default, context=context)


class tent_service_type(osv.Model):
    _name = "tent.service.type"
    _inherits = {'product.category':'ser_id'}
    _description = "Tipo de servicio"
    _columns = {
        'ser_id':fields.many2one('product.category', 'category', required=True, select=True, ondelete='cascade'),
    }
    _defaults = {
        'istentservicetype': 1,
    }

class tent_services(osv.Model):
    _name = 'tent.services'
    _description = 'Servicios de carpa'
    _inherits = {'product.template': 'service_id'}
    
    def costos_total(self, cursor, user, ids, name, arg, context=None):
            res = {}
            precision = self.pool.get('decimal.precision').precision_get(cursor, user, 'Account')
            for serv in self.browse(cursor, user, ids, context=context):
                res[serv.id] = round((serv.list_price+(serv.list_price*serv.taxes_id.amount)),precision)
            return res
                
    _columns = {
        'costo_total': fields.function(costos_total, string='Costo total', type='float'),
        'service_id': fields.many2one('product.template', 'Service_id', required=True, ondelete='cascade'),
    }
    _defaults = {
        'istentservice': 1,
    } 

class res_partner(osv.Model):
    _inherit= "res.partner"
    _columns= {
        'partner_id':fields.many2one('tent.reservation','Contactos'),
    }
    
class tent_reservation(osv.Model):
    _name = "tent.reservation"
    _rec_name = "reservation_no"
    _description = "Tent Reservation"
    _order = 'reservation_no desc'
    id_filter=[]
    
    def default_get(self, cr, uid, fields, context=None):
         if context is None:
             context = {}
         res = super(tent_reservation, self).default_get(cr, uid, fields, context=context)
         if context:
             keys = context.keys()
             if 'date' in keys:
                 fecha,hora=context['date'].split(' ')
                 a,m,d=fecha.split('-')
                 checkout=date(int(a),int(m),int(d)+1)
                 checkout=checkout.strftime("%Y-%m-%d")
                 checkout=checkout+' '+hora
                 res.update({'checkin': context['date']})
             if 'tent_id' in keys:
                 res.update({'reservation_tent_line':[(0, 0, {'reserve': [(6, 0, [int(context['tent_id'])])]})]})

         return res

    def duracion(self,cr,uid,checkin_date,checkout_date,context=None):
        duration_vals=self.onchange_dates(cr, uid, [], checkin_date=checkin_date, checkout_date=checkout_date, duration=False)
        duration = duration_vals.get('value', False) and duration_vals['value'].get('duration') or 0.0
        if duration == 0:
            duration = 1
        return duration 

    def sub_total(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        subtotal_tent=0
        subtotal_serv=0
        dias=1
        records=self.browse(cr,uid,ids)
        for r in records:
            dias=self.duracion(cr,uid,r.checkin,r.checkout,context=context)
            for h in r.reservation_tent_line:
                for lp in h.reserve:
                    subtotal_tent=subtotal_tent+lp.list_price
            for s in r.service_reservation_tent_line:
                subtotal_serv=subtotal_serv+(s.service_id.list_price*s.product_uom_qty)
            res[r.id]=(subtotal_tent+subtotal_serv)*dias
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
        iva_tent=0
        iva_serv=0
        dias=1
        cont=0
        records=self.browse(cr,uid,ids)
        for r in records:
            dias=self.duracion(cr,uid,r.checkin,r.checkout,context=context)
            for h in r.reservation_tent_line:
                for lp in h.reserve:
                    iva_tent=iva_tent+(lp.taxes_id.amount*lp.list_price)
            for s in r.service_reservation_tent_line:
                iva_serv=iva_serv+(s.service_id.taxes_id.amount*(s.product_uom_qty*s.service_id.list_price))
            res[r.id]=(iva_tent+iva_serv)*dias
        return res

    def cuenta_total(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        total_tent=0
        total_serv=0
        dias=1
        cont=0
        records=self.browse(cr,uid,ids)
        for r in records:
            dias=self.duracion(cr,uid,r.checkin,r.checkout,context=context)
            for h in r.reservation_tent_line:
                for ct in h.reserve:
                    total_tent=total_tent+ct.costo_total
            for s in r.service_reservation_tent_line:
                total_serv=total_serv+(s.service_id.costo_total*s.product_uom_qty)
            res[r.id]=(total_tent+total_serv)*dias        
        return res
        
    def dias_hospedaje(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        records=self.browse(cr,uid,ids)
        for r in records:
            res[r.id]=self.duracion(cr,uid,r.checkin,r.checkout,context=context)
        return res

    _columns = {
        'reservation_no': fields.char('Reservación N°', size=64, readonly=True),
        'date_order':fields.datetime('Fecha de la orden', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'warehouse_id':fields.many2one('stock.warehouse', 'Compañía', readonly=True, required=True, states={'draft':[('readonly', False)]}),
        'partner_id':fields.many2one('res.partner', 'Nombre del huesped', readonly=True, required=True, states={'draft':[('readonly', False)]}),
        'pricelist_id':fields.many2one('product.pricelist', 'Lista de precio', required=True, readonly=True, states={'draft':[('readonly', False)]}, help="Pricelist for current reservation. "),
        'partner_invoice_id':fields.many2one('res.partner', 'Dirección de facturación', readonly=True, states={'draft':[('readonly', False)]}, help="Invoice address for current reservation. "),
        'partner_order_id':fields.many2one('res.partner', 'Contacto', readonly=True, states={'draft':[('readonly', False)]}, help="The name and address of the contact that requested the order or quotation."),
        'partner_shipping_id':fields.many2one('res.partner', 'Dirección de envío', readonly=True, states={'draft':[('readonly', False)]}, help="Delivery address for current reservation. "),
        'checkin': fields.datetime('Fecha-llegada-prevista', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'checkout': fields.datetime('Fecha-salida-prevista', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'adults':fields.integer('Adultos', size=64, readonly=True, states={'draft':[('readonly', False)]}, help='List of adults there in guest list. '),
        'children':fields.integer('Niños', size=64, readonly=True, states={'draft':[('readonly', False)]}, help='Number of children there in guest list. '),
        'reservation_tent_line':fields.one2many('reservation_tent_line', 'line_id', 'Linea de reservación', help='Tent reservation details.'),
        'service_reservation_tent_line':fields.one2many('tent_reservation_service.line','serviline_id', 'Reservation Line', help='Tent service reservation details. '),
        'state': fields.selection([('draft', 'En espera'), ('confirm', 'Confirmado'),('invoiced', 'Facturado'),('paid', 'Pagado'), ('done', 'Finalizado'), ('cancel', 'Cancelado')], 'Estado', readonly=True),
        'dummy': fields.datetime('Dummy'),
        'sub_total':fields.function(sub_total,type='float',string='Sub Total'),
        'cuenta_iva':fields.function(cuentas_iva,type='float',string='IVA'),
        'cuenta_total':fields.function(cuenta_total,type='float',string='Total'),
        'acccount_invoice_id':fields.integer('Id de la factura',readonly=True,),
        'verificar_pago':fields.function(verificar_pago,int='float',string='Verificar Pago'),
        'fecha_salida': fields.datetime('Fecha de salida del cliente', readonly=True,),
        'dias_hospedaje':fields.function(dias_hospedaje,type='integer',string='Días de Hospedaje'),
        'child_ids':fields.one2many('res.partner','partner_id', 'Customers'),
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'date_order': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def create(self,cr,uid,values,context=None):
        values.update({
            'reservation_no':self.pool.get('ir.sequence').get(cr,uid,'tent.reservation')})
        return super(tent_reservation,self).create(cr,uid,values,context=context)
    def on_change_checkin(self, cr, uid, ids, date_order, checkin_date=time.strftime('%Y-%m-%d %H:%M:%S'),checkout_date=time.strftime('%Y-%m-%d %H:%M:%S'), context=None):
        if date_order and checkin_date:
            if checkin_date < date_order:
                raise osv.except_osv(_('Warning'), _('Checkin date should be greater than the current date.'))
        return {'value':{'dias_hospedaje':self.duracion(cr,uid,checkin_date,checkout_date,context=context)}}

    def on_change_checkout(self, cr, uid, ids, checkin_date=time.strftime('%Y-%m-%d %H:%M:%S'), checkout_date=time.strftime('%Y-%m-%d %H:%M:%S'), context=None):
        if not (checkout_date and checkin_date):
            return {'value':{}}
        if checkout_date < checkin_date:
            raise osv.except_osv(_('Warning'), _('Checkout date should be greater than the Checkin date.'))
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
        self.write(cr, uid, ids, {'state':'cancel'},context=context)
        return True
    def reservation_done(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state':'done','fecha_salida':datetime.now()},context=context)
        return True
    def draft_reservation(self,cr,uid,ids):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
        
    def confirmed_reservation(self,cr,uid,ids,context=None):
        tent_reservation_line_vals=[]
        tent_reservation_line_obj=self.pool.get('tent.reservation.line')
        for reservation in self.browse(cr, uid, ids,context=context):
            for h in reservation.reservation_tent_line:
                for tent in h.reserve:
                    tent_reservation_line_vals={
                                'tent_id':tent.id,
                                'check_in':reservation.checkin,
                                'check_out':reservation.checkout,
                                'state':'assigned',
                                'reservation_id':reservation.id
                                }
                    tent_reservation_line_obj.create(cr, uid, tent_reservation_line_vals, context=context)
        self.write(cr, uid, ids, {'state':'confirm'},context=context)
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
            for line in reservation.reservation_tent_line:
                for r in line.reserve:
                    tax= [t.id for t in r.taxes_id]
                    #~ Aqui Adicionamos la variable que contendra los valores de account invoiced line por cada reserva
                    account_line_vals.append(list((0,False,{
                        'uos_id': r.product_id.uos_id and r.product_id.uos_id.id, 
                        'account_id': account_line_data.id, 
                        'price_unit': r['lst_price'], 
                        'quantity': duration,
                        'invoice_line_tax_id': [[6, False, [tax[0]]]], 
                        'product_id': r.product_id and r.product_id.id, 
                        'name': r.name, 
                        'account_analytic_id': False, 
                        })))
                    
            for line in reservation.service_reservation_tent_line:
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
                
    def on_change_filter(self, cr, uid, ids, reservation_tent_line, context=None):
        tent_reservation.id_filter=[]
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
                            tent_reservation.id_filter=list_id
        return True


class reservation_tent_line(osv.Model):
    _name = "reservation_tent_line"
    _description = "Tent Reservation Line"
    _columns = {
         'name':fields.char('Name', size=64),
         'line_id':fields.many2one('tent.reservation'),
         'reserve':fields.many2many('tent.tent', 'tent_reservation_line_rel', 'tent_id', 'tent_reservation_line_id', domain="[('istent','=',True),('categ_id','=',categ_id)]"),
         'categ_id': fields.many2one('product.category', 'Tent Type', domain="[('istenttype','=',True)]", change_default=True),
        }

    def on_change_categ(self, cr, uid, ids, categ_ids, checkin, checkout, context=None):
        tent_obj = self.pool.get('tent.tent')
        h_tent_ids = tent_obj.search(cr, uid, [('categ_id', '=', categ_ids)], context=context)
        assigned = False
        tent_ids = []
        if not checkin:
            raise osv.except_osv(_('No Checkin date Defined!'), _('Before choosing a room,\n You have to select a Check in date or a Check out date in the reservation form.'))
        for tent in tent_obj.browse(cr, uid, h_tent_ids, context=context):
            assigned = False
            for line in tent.tent_reservation_line_ids:
                if line.check_in == checkin and line.check_out == checkout:
                    assigned = True
            if not assigned:
                tent_ids.append(tent.id)
        if type(categ_ids) == int:
            tent_idt=tuple(tent_ids)
            if tent_ids:
                cr.execute("select tent_reservation_line_id from tent_reservation as tr " \
                    "inner join reservation_tent_line as trl on trl.line_id = tr.id " \
                    "inner join tent_reservation_line_rel as trlr on trlr.tent_id = trl.id " \
                    "where (checkin,checkout) overlaps ( timestamp %s , timestamp %s ) " \
                    "and trlr.tent_reservation_line_id  in %s and categ_id=cast(%s as integer) " \
                    "and tr.state<>'cancel'"\
                    ,(str(checkin),str(checkout),tent_idt,categ_ids)
                          )
                for row in cr.fetchall():
                    row=set(row)
                    tent_ids=set(tent_ids)
                    tent_ids=tent_ids-row

        domain = {'reserve': [('id', 'in', list(tent_ids)),('id', '!=', list(tent_reservation.id_filter))]}
        
        return {'domain': domain}
    
    def consult_booking(self, cr, uid, ids, checkin, checkout, booking_adult, booking_child, context=None):
        tent_obj = self.pool.get('tent.tent')
        h_tent_ids = tent_obj.search(cr, uid, [('max_adult', '>=', booking_adult), ('max_child', '>=', booking_child), ('website_published', '=', True)], context=context)
        assigned = False
        tent_ids = []
        if not checkin:
            raise osv.except_osv(_('No Checkin date Defined!'), _('Before choosing a room,\n You have to select a Check in date or a Check out date in the reservation form.'))
        for tent in tent_obj.browse(cr, uid, h_tent_ids, context=context):
            assigned = False
            for line in tent.tent_reservation_line_ids:
                if line.check_in == checkin and line.check_out == checkout:
                    assigned = True
            if not assigned:
                tent_ids.append(tent.id)
        tent_idt=tuple(tent_ids)
        if tent_ids:
            cr.execute("select tent_reservation_line_id from tent_reservation as tr " \
                "inner join reservation_tent_line as trl on trl.line_id = tr.id " \
                "inner join tent_reservation_line_rel as trlr on trlr.tent_id = trl.id " \
                "where (checkin,checkout) overlaps ( timestamp %s , timestamp %s ) " \
                "and trlr.tent_reservation_line_id  in %s and tr.state<>'cancel'"\
                ,(str(checkin),str(checkout),tent_idt)
                      )
            for row in cr.fetchall():
                row=set(row)
                tent_ids=set(tent_ids)
                tent_ids=tent_ids-row

        
        return list(tent_ids)

class tent_reservation_line(osv.Model):
    _name = 'tent.reservation.line'
    _description = 'Tent Reservation'
    _rec_name = 'tent_id'
    _columns = {
        'tent_id': fields.many2one('tent.tent', 'tent id'),
        'check_in':fields.datetime('Check In Date', required=True),
        'check_out': fields.datetime('Check Out Date', required=True),
        'state': fields.selection([('assigned', 'Assigned'), ('unassigned', 'Unassigned')], 'Tent Status'),
        'reservation_id': fields.many2one('tent.reservation', 'Reservation'),
    }

tent_reservation_line()


class tent_resv(osv.Model):
    _inherit = 'tent.tent'
    _description = 'Tent resv'
    _columns = {
        'tent_reservation_line_ids': fields.one2many('tent.reservation.line', 'tent_id', 'Tent Reservation Line'),
    }

class tent_reservation_summary(osv.Model):
     _name = 'tent.reservation.summary'
     _description = 'Tent reservation summary'
     _columns = {
         'date_tent_from':fields.datetime('Tent Date From'),
         'date_tent_to':fields.datetime('Tent Date To'),
         'summary_tent_header':fields.text('Summary Tent Header'),
         'tent_summary':fields.text('Tent Summary'),
     }
 
     def tent_reservation(self, cr, uid, ids, context=None):
         mod_obj = self.pool.get('ir.model.data')
         if context is None:
             context = {}
         model_data_ids = mod_obj.search(cr, uid, [('model', '=', 'ir.ui.view'), ('name', '=', 'view_tent_reservation_form')], context=context)
         resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
         return {
             'name': _('Reconcile Write-Off'),
             'context': context,
             'view_type': 'form',
             'view_mode': 'form',
             'res_model': 'tent.reservation',
             'views': [(resource_id, 'form')],
             'type': 'ir.actions.act_window',
             'target': 'new',
         }
         
     def get_tent_summary(self, cr, uid, ids, date_from, date_to, context=None):
 
         res = {}
         all_detail = []
         tent_obj = self.pool.get('tent.tent')
         reservation_line_obj = self.pool.get('tent.reservation.line')
         date_range_list = []
         main_header = []
         summary_header_list = ['Tents']
         if date_from and date_to:
             if date_from > date_to:
                 raise osv.except_osv(_('User Error!'), _('Please Check Time period Date From can\'t be greater than Date To !'))
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
             tent_ids = tent_obj.search(cr, uid, [], context=context)
             all_tent_detail = []
             for tent in tent_obj.browse(cr, uid, tent_ids, context=context):
                 tent_detail = {}
                 tent_list_stats = []
                 tent_detail.update({'name':tent.name or ''})
                 if not tent.tent_reservation_line_ids:
                     for chk_date in date_range_list:
                         tent_list_stats.append({'state':'Free', 'date':chk_date, 'tent_id':tent.id})
                 else:
                     for chk_date in date_range_list:
                         for tent_res_line in tent.tent_reservation_line_ids:
                             tent_reservation_line_ids = [i.id for i in tent.tent_reservation_line_ids]
                             
                             tent_reservation_line_ids = reservation_line_obj.search(cr, uid, [('id', 'in', tent_reservation_line_ids), ('check_in', '<=', chk_date), ('check_out', '>=', chk_date)])
                             if tent_reservation_line_ids:
                                 tent_list_stats.append({'state':'Reserved', 'date':chk_date, 'tent_id':tent.id})
                                 break
                             else:
                                 tent_list_stats.append({'state':'Free', 'date':chk_date, 'tent_id':tent.id})
                                 break
                 tent_detail.update({'value':tent_list_stats})
                 all_tent_detail.append(tent_detail)
             main_header.append({'header':summary_header_list})
             res.update({'value':{'summary_tent_header': str(main_header), 'tent_summary':str(all_tent_detail)}})
         return res

class tent_service_line(osv.Model):
    _name = 'tent_reservation_service.line'
    _description = "Tent Reservation Service Line"
    
    def limpiar_selector(self, cr, uid, ids,context=None):
        res={}
        res = {
        'service_id':'',
                }
        return {'value':res}
        
    _columns = {
        'name':fields.char('Name', size=64),
        'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        'categ_id': fields.many2one('product.category', 'Service Type', domain="[('istentservicetype','=',True)]", change_default=True),
        'serviline_id':fields.many2one('tent.reservation'),
        'service_id':fields.many2one('tent.services',"Services"),
        }

class res_company(osv.Model):
    _inherit = 'res.company'
    _columns = {
        'additional_hours': fields.integer('Additional Hours', help="Provide the min hours value for check in, checkout days, whatever the hours will be provided here based on that extra days will be calculated."),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
