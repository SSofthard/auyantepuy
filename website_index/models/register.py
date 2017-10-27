# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from datetime import datetime, date, time, timedelta
import time
from openerp import http, SUPERUSER_ID


class res_partner(osv.Model):
    _inherit = 'res.partner'
    
    
    def vacumm_token(self,cr,uid):
        register_obj = self.pool.get('res.partner')
        register_id= register_obj.search(cr,SUPERUSER_ID,[('signup_expiration','<',time.strftime('%Y-%m-%d %H:%M:%S'))])
        users_obj = self.pool.get('res.users')
        users_id = users_obj.search(cr,SUPERUSER_ID,[('partner_id','=',register_id)])

        delete_user_id=users_obj.unlink(cr,SUPERUSER_ID,users_id)
        delete_id=register_obj.unlink(cr,SUPERUSER_ID,register_id)
        
        
