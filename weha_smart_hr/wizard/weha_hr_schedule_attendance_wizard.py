# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning, ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class WehaWizardHrScheduleAttendance(models.TransientModel):
    _name= "weha.wizard.hr.schedule.attendance"

    day = fields.Date('Date', default=datetime.now())

    def process(self):
        active_id = self.env.context.get('active_id') or False
        schedule_ids = self.env['weha.hr.schedule'].search([('day','=', self.day)])
        for schedule_id in schedule_ids:
            schedule_id.action_check_attendance()
