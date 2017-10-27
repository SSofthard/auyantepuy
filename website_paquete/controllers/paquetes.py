# -*- coding: utf-8 -*-

from openerp import http
from openerp.addons.web.controllers import main
from openerp.http import request
from openerp import SUPERUSER_ID
from openerp.addons.website_crm.controllers.main import contactus



class paquetes(http.Controller):
    @http.route(['/paquetes', '/paquetes/page/<int:page>'], type='http', auth='public', website=True)
    def paquete(self,**searches):
        cr, uid, context = http.request.cr, http.request.uid, http.request.context
        #~ con la variable searches guardo las claves y los valores que paso desde la vista al controlador
        #~ y los que cargo por defectos en la primera carga
        #~ empiezo con destino, por defecto la categoria es Destinos y primero que cargo es Isla de Margarita    
        searches.setdefault('destino', ['Isla la Tortuga','Destinos'])
        #~ con esto busco los hijos de la Categoria Destino de producto
        #~ con este arreglo guardo los nombres de las categorias
        name_data=[]
        imagen_data={}
        destinos_obj = http.request.registry['product.category']
        destino_ids=destinos_obj.search(cr,SUPERUSER_ID,[('name','in',searches['destino'])],order="id asc",context=context)
        searches.setdefault('destino_id',destino_ids[1])
        destinos_ids=destinos_obj.search(cr,SUPERUSER_ID,[('parent_id','=',destino_ids[0])],context=context)
        destino_data=destinos_obj.browse(cr,SUPERUSER_ID,destinos_ids,context=context)
        #~ con esto separo los nombre en una lista con su respectivo id ejemplo [['id':18,'name':['Isla','de','Margarita']]...] 
        #~ para poder cumplir con el estructura del diseño.... 
        for data in destino_data:
            lista=data.name.split()
            name_data.append({'destino_id':str(data.id),'name':lista})
        #~ con esto busco los paquetes
        product_obj = http.request.registry['product.template']
        product_ids=product_obj.search(cr,SUPERUSER_ID,[('categ_id','=',int(searches['destino_id']))],context=context)
        searches.setdefault('product_id', product_ids[0])
        product_data=product_obj.browse(cr,SUPERUSER_ID,product_ids,context=context)
        for data in product_data:
            if data.id == int(searches['product_id']):
                imagen_data = data.images
                caracteristicas_data=data
        #~ cambio el id de unicode a int para el dyc searches
        searches['product_id']=int(searches['product_id'])
       
        return http.request.website.render('website_paquete.paquetes', {
            'destinos':destino_data,
            'name_data':name_data,
            'product_data':product_data,
            'caracteristicas_data':caracteristicas_data,
            'searches':searches,
            'imagen_data':imagen_data,
            'uid':uid
        })


    @http.route(['/paquetes/contacto'], type='http', auth='public', website=True)
    def reserva_paquete(self, **kwargs):
        cr, SUPERUSER_ID, context = http.request.cr, http.request.uid, http.request.context

        contact_name=kwargs['contact_name']
        phone=kwargs['contact_phone']
        email_from=kwargs['contact_email']
        description="Descripcion de Reserva:\n\nPaquete seleccionado:"+kwargs['paquete_name']+".\nFecha:"+kwargs['reserva_checkin']+"\nCantidad de adultos:"+kwargs['num_adultos']+".\nCantidad de ninos:"+kwargs['num_ninos']+"."

        kwargs = {
            'contact_name':contact_name,
            'phone':phone,
            'email_from':email_from,
            'description':description,
        }
        
        return contactus().contactus(self, **kwargs)

    
