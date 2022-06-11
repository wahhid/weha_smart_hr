# -*- coding: utf-8 -*-
# Part of WEHA Consultant.

from odoo import fields, http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from collections import OrderedDict
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.mail import _message_post_helper
import json
import base64
import werkzeug
import logging
_logger = logging.getLogger(__name__)


class PortalHr(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalHr, self)._prepare_portal_layout_values()
        domain = []
        attendance_count = request.env['hr.attendance'].sudo().search_count(domain)
        attendances = request.env['hr.attendance'].sudo().search(domain)
        values['attendance_count'] = attendance_count
        values['attendances'] = attendances
        return values

    @http.route(['/my/attendances/<int:attendance_id>'], type='http', auth="public", website=True)
    def portal_my_ticket_detail(self, attendance_id, access_token=None, report_type=None, message=False, download=False, **kw):
        try:
            hr_attendance_sudo = self._document_check_access(
                'hr.attendance', attendance_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        values = {
            'token': access_token,
            'ticket': hr_attendance_sudo,
            'message': message,
            'bootstrap_formatting': True,
            'partner_id': hr_attendance_sudo.partner_id.id,
            'report_type': 'html',
        }

        return request.render("weha_smart_hr.portal_attendance_page", values)


        