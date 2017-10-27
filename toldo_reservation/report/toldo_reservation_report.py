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
            'get_awning_type':self._get_awning_type,
            'get_awning_nos':self._get_awning_nos,
            'get_awning_used_detail':self._get_awning_used_detail,
        })
        self.context = context

    def _get_awning_type(self, reservation_line):
        awning_types = ''
        for line in reservation_line:
            if line.categ_id:
                awning_types += line.categ_id.name
                awning_types += ' '

        return awning_types

    def _get_awning_nos(self, reservation_line):
        awning_nos = ''
        for line in reservation_line:
            for awning in line.reserve:
                awning_nos += awning.name
                awning_nos += ' '
        return awning_nos

    def get_data(self, date_start, date_end):
        reservation_obj = self.pool.get('awning.reservation')
        tids = reservation_obj.search(self.cr, self.uid, [('checkin', '>=', date_start), ('checkout', '<=', date_end)])
        res = reservation_obj.browse(self.cr, self.uid, tids)
        return res

    def get_checkin(self, date_start, date_end):
        reservation_obj = self.pool.get('awning.reservation')
        tids = reservation_obj.search(self.cr, self.uid, [('checkin', '>=', date_start), ('checkin', '<=', date_end)])
        res = reservation_obj.browse(self.cr, self.uid, tids)
        return res

    def get_checkout(self, date_start, date_end):
        reservation_obj = self.pool.get('awning.reservation')
        tids = reservation_obj.search(self.cr, self.uid, [('checkout', '>=', date_start), ('checkout', '<=', date_end)])
        res = reservation_obj.browse(self.cr, self.uid, tids)
        return res

    def _get_awning_used_detail(self, date_start, date_end):
        awning_used_details = []
        toldo_awning_obj = self.pool.get('toldo.awning')
        awning_ids = toldo_awning_obj.search(self.cr, self.uid, [])
        for awning in toldo_awning_obj.browse(self.cr, self.uid, awning_ids):
            counter = 0
            details = {}
            if awning.awning_reservation_line_ids:
                for awning_resv_line in awning.awning_reservation_line_ids:
                    if awning_resv_line.check_in >= date_start and awning_resv_line.check_in <= date_end:
                        counter += 1
                if counter >= 1:
                    details.update({'name': awning.name or '', 'no_of_times_used': counter})
                    awning_used_details.append(details)

        return awning_used_details

class report_test_checkin(osv.AbstractModel):
    _name = "report.toldo_reservation.report_checkin_qweb"
    _inherit = "report.abstract_report"
    _template = "toldo_reservation.report_checkin_qweb"
    _wrapped_report_class = reservation_detail_report

class report_test_checkout(osv.AbstractModel):
    _name = "report.toldo_reservation.report_checkout_qweb"
    _inherit = "report.abstract_report"
    _template = "toldo_reservation.report_checkout_qweb"
    _wrapped_report_class = reservation_detail_report

class report_test_maxawning(osv.AbstractModel):
    _name = "report.toldo_reservation.report_maxawning_qweb"
    _inherit = "report.abstract_report"
    _template = "toldo_reservation.report_maxawning_qweb"
    _wrapped_report_class = reservation_detail_report

class report_test_awningres(osv.AbstractModel):
    _name = "report.toldo_reservation.report_awningres_qweb"
    _inherit = "report.abstract_report"
    _template = "toldo_reservation.report_awningres_qweb"
    _wrapped_report_class = reservation_detail_report
# report_sxw.report_sxw('report.reservation.detail', 'toldo.reservation', 'addons/toldo_reservation/report/awning_res.rml', parser=reservation_detail_report)
# report_sxw.report_sxw('report.checkin.detail', 'toldo.reservation', 'addons/toldo_reservation/report/checkinlist.rml', parser=reservation_detail_report)
# report_sxw.report_sxw('report.checkout.detail', 'toldo.reservation', 'addons/toldo_reservation/report/checkoutlist.rml', parser=reservation_detail_report)
# report_sxw.report_sxw('report.maxawning.detail', 'toldo.reservation', 'addons/toldo_reservation/report/maxawning.rml', parser=reservation_detail_report)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
