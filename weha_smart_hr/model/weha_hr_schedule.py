from odoo import models, fields, api 
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

from datetime import datetime, time, timedelta
import pytz
import logging

import math

_logger = logging.getLogger(__name__)


AVAILABLE_SCHEDULE_STATES = [
    ('draft', 'Draft'),
    ('validate', 'Confirmed'),
    ('exception', 'Exception'),
    ('request', 'Request'),
    ('locked', 'Locked'),
    ('unlocked', 'Unlocked'),
]

AVAILABLE_SCHEDULE_DETAIL_STATES = [
    ('draft', 'Draft'),
    ('validate', 'Confirmed'),
    ('exception', 'Exception'),
    ('locked', 'Locked'),
    ('unlocked', 'Unlocked'),
]

DAYOFWEEK_SELECTION = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
]


class WehaHrScheduleTemplate(models.Model):
    _name = 'weha.hr.schedule.template'

    name  = fields.Char('Name', size=100, required=True)
    code = fields.Char('Code', size=10, required=True)
    time_start = fields.Float('Start Time')
    time_end = fields.Float('End Time')
    hours = fields.Float('Hours')

class WehaHrSchedule(models.Model):
    _name = 'weha.hr.schedule'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    def name_get(self):
        result = []
        for record in self:
            name = record.day.strftime('%d-%m-%Y') + ' (' + record.schedule_template_id.name + ')'
            result.append((record.id, name))
        return result


    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return str(factor * int(math.floor(val))).zfill(2), str(int(round((val % 1) * 60))).zfill(2)

    @api.onchange('schedule_template_id')
    def _onchange_schedule_template_id(self):
        if self.day:
            user_tz = self.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            hours, minutes  = self.float_time_convert(self.schedule_template_id.time_start)
            local_date_time = datetime.strptime(self.day.strftime('%Y-%m-%d')  + " " + hours + ":" + minutes + ":00", DEFAULT_SERVER_DATETIME_FORMAT)
            self.date_time_start = local_date_time + timedelta(hours=-7)
            hours, minutes  = self.float_time_convert(self.schedule_template_id.time_end) 
            _logger.info(hours)
            _logger.info(minutes)
            local_date_time = datetime.strptime(self.day.strftime('%Y-%m-%d')  + " " + hours + ":" + minutes + ":00", DEFAULT_SERVER_DATETIME_FORMAT)
            _logger.info(local_date_time)
            self.date_time_end = local_date_time + timedelta(hours=-7)

    def action_check_attendance(self):
        self.message_post(body="CHeck Attendance")
        if self.state != 'locked':
            # domain = [
            #     ('employee_id', '=', self.employee_id.id),
            #     ('check_in', '>=', self.day.strftime(DEFAULT_SERVER_DATE_FORMAT) + " 00:00:00"),
            #     ('check_in', '<=', self.day.strftime(DEFAULT_SERVER_DATE_FORMAT) + " 23:59:00"),
            # ]
            #Clear Exception
            self.exception_ids.unlink()
            domain = [
                ('employee_id', '=', self.employee_id.id),
                ('check_in', '>=', self.day.strftime(DEFAULT_SERVER_DATE_FORMAT) + " 00:00:00"),
                ('check_in', '<=', self.day.strftime(DEFAULT_SERVER_DATE_FORMAT) + " 23:59:00"),
            ]

            hr_attendance_id = self.env['hr.attendance'].search(domain, limit=1)
            if hr_attendance_id:
                _logger.info(hr_attendance_id.employee_id.name)
                self.hr_attendance_id = hr_attendance_id.id
                self.actual_check_in = hr_attendance_id.check_in
                self.actual_check_out = hr_attendance_id.check_out

                _logger.info(self.actual_check_in)
                _logger.info(self.date_time_start)

                is_exception = False
                #Clear Exception
                self.write({'exception_ids': [(5,)]})  
                exception_ids = []
                if self.actual_check_in and self.actual_check_in > self.date_time_start:
                    is_exception = True
                    _logger.info('Add Late In Exception')
                    values = (0,0,{
                        'schedule_id': self.id,
                        'exception_code': 'latein',
                    })
                    exception_ids.append(values)
                    #self.write({'exception_ids': values})     
                if self.actual_check_out and self.actual_check_out < self.date_time_end:
                    is_exception = True
                    _logger.info('Add Early Out Exception')
                    values = (0,0,{
                        'schedule_id': self.id,
                        'exception_code': 'earlyout',
                    })
                    exception_ids.append(values)
                    #self.write({'exception_ids': values}) 
                
                if is_exception:
                    self.state = 'exception'
                    self.write({'exception_ids': exception_ids}) 
                else:
                    self.state = 'locked'
            else:
                exception_ids = []
                values = (0,0,{
                        'schedule_id': self.id,
                        'exception_code': 'noswapin',
                })
                exception_ids.append(values)
                values = (0,0,{
                        'schedule_id': self.id,
                        'exception_code': 'noswapout',
                })
                exception_ids.append(values)
                self.state = 'exception'
                self.write({'exception_ids': exception_ids})


    def action_request_exception(self):
        pass
    
    #name = fields.Char('Name',size=50, required=True, readonly=True, states={'draft': [('readonly', False)]})
    color = fields.Integer()
    company_id = fields.Many2one('res.company','Company', readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', related='employee_id.department_id', store=True)
    employee_id = fields.Many2one('hr.employee','Employee', required=True, readonly=True, states={'draft': [('readonly', False)]})
    #template_id = fields.Many2one('resource.calendar', 'Schedule Template', readonly=True, states={'draft': [('readonly', False)]})
    schedule_template_id = fields.Many2one('weha.hr.schedule.template','Schedule Template', required=True)
    day = fields.Date('Day', required=True)
    date_time_start = fields.Datetime('Start Date Time', required=False, readonly=True)
    date_time_end = fields.Datetime('End Date Time', required=False, readonly=True)
    hr_attendance_id = fields.Many2one('hr.attendance', 'Attendance', readonly=True)
    actual_check_in = fields.Datetime('Actual Check In', readonly=True)
    actual_check_out = fields.Datetime('Actual Check Out', readonly=True)

    #Exception Employee
    exception_description = fields.Text('Exception Description', readonly=True)
    
    #Exception Approval
    approved_datetime = fields.Datetime('Approved/Rejected Date', readonly=True)
    approved_state = fields.Selection([
                                        ('approve', 'Approve'),
                                        ('reject', 'Reject'),
                                        ], readonly=True)
    approved_by = fields.Many2one('hr.employee', 'Approved By', readonly=True)
    approved_reason = fields.Text('Rejected Reason', reaodnly=True)

    exception_ids = fields.Many2many(
        'weha.hr.schedule.exception', 
        'weha_hr_schedule_hr_exception_rel', 
        'schedule_id', 
        'exception_id', 
        string='Exceptions'
    )

    state = fields.Selection(AVAILABLE_SCHEDULE_STATES, 'Status', required=True, readonly=True, default='draft', tracking=True)

    _sql_constraints = [
        ('day_employee_id_uniq', 'UNIQUE (day, employee_id)',  'You can not have same day for employee !')
    ]

# class WehaHrScheduleDetail(models.Model):
#     _name = 'weha.hr.schedule.detail'
#     _inherit = 'mail.thread'
#     _description = 'HR Schedule Detail'
#     _order = 'day asc'


#     name = fields.Char('Name', size=64, required=True)
#     dayofweek = fields.Selection(DAYOFWEEK_SELECTION, 'Day of Week', required=True, default=0)
#     shift_id = fields.Many2one('hr.schedule.shift', 'Shift', required=False)
#     date_start = fields.Datetime('Start Date', required=False)
#     date_end = fields.Datetime('End Date', required=False)
#     day = fields.Date('Day', required=True)
#     schedule_id = fields.Many2one('weha.hr.schedule','Schedule', required=True)
#     type = fields.Selection([('work','Work'),('off','Off'),('holiday','Holiday')],'Type', required=True, default='work')
#     employee_id = fields.Many2one('hr.employee', 'Employee', related='schedule_id.employee_id', store=True)
#     department_id = fields.Many2one('hr.department','Department', related='schedule_id.department_id', store=True)
#     state = fields.Selection(AVAILABLE_SCHEDULE_DETAIL_STATES, 'Status', required=True, readonly=True, default='draft')

#     actual_in = fields.Datetime('Actual In')
#     actual_out = fields.Datetime('Actual Out')

#     working_hours = fields.Integer('Hours', default=0)

#     schedule_hours = fields.Integer('Schedule Hours', default=0)

#     diff_hours = fields.Integer('Different')

#     diff_late_in = fields.Integer(compute='_calculate_diff_late_in', string='Diff Late In')

#     hours_before_in = fields.Integer('Hours Before In', default=0)

#     hours_after_out = fields.Integer('Hours After Out', default=0)

#     absence_ids = fields.One2many('hr.absence','schedule_detail_id', 'Absences')
#     exception_ids = fields.One2many('hr.schedule.exception', 'schedule_detail_id','Exceptions')


class WehaHrScheduleException(models.Model):
    _name = 'weha.hr.schedule.exception'
    _rec_name = 'exception_code'

    schedule_id = fields.Many2one('weha.hr.schedule','Schedule #', readonly=True)
    employee_id = fields.Many2one('hr.employee','Employee', related='schedule_id.employee_id', readonly=True)
    day = fields.Date(string='Date', store=True, related='schedule_id.day',readonly=True)
    exception_code = fields.Selection([('normal', 'Normal'),
                                       ('normexcept', 'Normal with Exception'),
                                       ('noswapin', 'No Swap-In'),
                                       ('noswapout', 'No Swap-Out'),
                                       ('latein', 'Late In'),
                                       ('earlyout', 'Early Out'), ], 'Exception')
    #exception_request_date = fields.Datetime('Exception Request Date', readonly=True)
    #exception_reason = fields.Selection([
    #                                        ('01','Dinas Luar Non Fullday/Non Fullboard'),
    #                                        ('02','Dinas Luar Fullday/Fullboard'),
    #                                        ('03','Cuti'),
    #                                        ('04', 'Ijin'),
    #                                        ('05', 'Ijin Sakit'),
    #                                        ('06','Tugas Belajar'),
    #                                        ('99', 'Lain - Lain')
    #                                    ], 'Exception Reason', readonly=True)
