# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class WehaWizardHrScheduleException(models.TransientModel):
    _name= "weha.wizard.hr.schedule.exception"

    exception_description = fields.Text('Exception Description', readonly=False)

    def process(self):
        active_id = self.env.context.get('active_id') or False
        schedule_id = self.env['weha.hr.schedule'].browse(active_id)
        schedule_id.sudo().write({'exception_description': self.exception_description, 'state': 'request'})



class WehaWizardHrScheduleExceptionApproval(models.TransientModel):
    _name= "weha.wizard.hr.schedule.exception.approval"

    approved_state = fields.Selection([('approve', 'Approve'),('reject', 'Reject')], 'Approval', default='approve')
    approved_reason = fields.Text('Rejected Reason')

    def process(self):
        active_id = self.env.context.get('active_id') or False
        schedule_id = self.env['weha.hr.schedule'].browse(active_id)
        employee_id = self.env['hr.employee'].search([('user_id','=', self.env.uid)])
        schedule_id.sudo().write(
            {
                'approved_datetime': datetime.now(),
                'approved_state': self.approved_state,
                'approved_reason': self.approved_reason,
                'approved_by': employee_id.id,
                'state': 'locked',
            }
        )
