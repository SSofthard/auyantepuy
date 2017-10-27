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
from openerp.osv import osv
import time
from openerp.report import report_sxw

class reservation_detail_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(reservation_detail_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_data': self.get_data,
            'get_checkin': self.get_checkin,
            'get_checkout': self.get_checkout,
            'get_tent_type':self._get_tent_type,
            'get_tent_nos':self._get_tent_nos,
            'get_tent_used_detail':self._get_tent_used_detail,
        })
        self.context = context

    def _get_tent_type(self, reservation_tent_line):
        tent_types = ''
        for line in reservation_tent_line:
            if line.categ_id:
                tent_types += line.categ_id.name
                tent_types += ' '

        return tent_types

    def _get_tent_nos(self, reservation_tent_line):
        tent_nos = ''
        for line in reservation_tent_line:
            for tent in line.reserve:
                tent_nos += tent.name
                tent_nos += ' '
        return tent_nos

    def get_data(self, date_start, date_end):
        reservation_obj = self.pool.get('tent.reservation')
        tids = reservation_obj.search(self.cr, self.uid, [('checkin', '>=', date_start), ('checkout', '<=', date_end)])
        res = reservation_obj.browse(self.cr, self.uid, tids)
        return res

    def get_checkin(self, date_start, date_end):
        reservation_obj = self.pool.get('tent.reservation')
        tids = reservation_obj.search(self.cr, self.uid, [('checkin', '>=', date_start), ('checkin', '<=', date_end)])
        res = reservation_obj.browse(self.cr, self.uid, tids)
        return res

    def get_checkout(self, date_start, date_end):
        reservation_obj = self.pool.get('tent.reservation')
        tids = reservation_obj.search(self.cr, self.uid, [('checkout', '>=', date_start), ('checkout', '<=', date_end)])
        res = reservation_obj.browse(self.cr, self.uid, tids)
        return res

    def _get_tent_used_detail(self, date_start, date_end):
        tent_used_details = []
        tent_tent_obj = self.pool.get('tent.tent')
        tent_ids = tent_tent_obj.search(self.cr, self.uid, [])
        for tent in tent_tent_obj.browse(self.cr, self.uid, tent_ids):
            counter = 0
            details = {}
            if tent.tent_reservation_line_ids:
                for tent_resv_line in tent.tent_reservation_line_ids:
                    if tent_resv_line.check_in >= date_start and tent_resv_line.check_in <= date_end:
                        counter += 1
                if counter >= 1:
                    details.update({'name': tent.name or '', 'no_of_times_used': counter})
                    tent_used_details.append(details)

        return tent_used_details

class report_test_checkin(osv.AbstractModel):
    _name = "report.tent.report_checkin_qweb"
    _inherit = "report.abstract_report"
    _template = "tent.report_checkin_qweb"
    _wrapped_report_class = reservation_detail_report

class report_test_checkout(osv.AbstractModel):
    _name = "report.tent.report_checkout_qweb"
    _inherit = "report.abstract_report"
    _template = "tent.report_checkout_qweb"
    _wrapped_report_class = reservation_detail_report

class report_test_maxroom(osv.AbstractModel):
    _name = "report.tent.report_maxtent_qweb"
    _inherit = "report.abstract_report"
    _template = "tent.report_maxtent_qweb"
    _wrapped_report_class = reservation_detail_report

class report_test_tentres(osv.AbstractModel):
    _name = "report.tent.report_tentres_qweb"
    _inherit = "report.abstract_report"
    _template = "tent.report_tentres_qweb"
    _wrapped_report_class = reservation_detail_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
