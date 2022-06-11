# -*- coding: utf-8 -*-
# Part of WEHA Consultant.

import re
import ast
import functools
import logging
import json
import werkzeug.wrappers
from datetime import datetime, date
from odoo.exceptions import AccessError
from odoo.addons.weha_smart_hr.common import invalid_response, valid_response
from odoo import http
from odoo.addons.weha_smart_hr.common import (
    extract_arguments,
    invalid_response,
    valid_response,
)


from odoo.http import request

_logger = logging.getLogger(__name__)

def validate_token(func):
    """."""

    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = (
            request.env["api.access_token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)
        )

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


class SmartHRController(http.Controller):
    
    @validate_token
    @http.route("/api/hr/v1.0/schedule", type="http", auth="none", methods=["POST"], csrf=False)
    def employee_schedule(self, **post):
        user_id = int(post['uid'])
        employee_id = request.env['hr.employee'].sudo().search([('user_id','=', user_id)], limit=1)
        if not employee_id:
            return invalid_response("Employee not found","Employee not found", 404)
        hr_schedule_ids = request.env['weha.hr.schedule'].sudo().search([('employee_id','=', employee_id.id)])
        if not hr_schedule_ids:
            return invalid_response("Schedule not found","Schedule not found", 404)
        data = []
        for hr_schedule_id in hr_schedule_ids:
            data.append(
                {'id': hr_schedule_id.id}
            )
        return valid_response(data, 200)
        

    @validate_token
    @http.route("/api/hr/v1.0/getuserbyuid", type="http", auth="none", methods=["POST"], csrf=False)
    def getuserbyuid(self, **post):
        _logger.info(post)
        uid = int(post['uid'])
        res_user_id = request.env['res.users'].browse(uid)
        if not res_user_id:
            return invalid_response("User not found","User not found", 404)
        data = {
            'id': res_user_id.id,
            'login': res_user_id.login,
            'name': res_user_id.name,
        }
        return valid_response(data, 200)
    

    @validate_token
    @http.route("/api/hr/v1.0/attcheck", type="http", auth="none", methods=["POST"], csrf=False)
    def attendance_check(self, **post):
        employee_id = int(post['employee_id'])
        employee = request.env['hr.employee'].browse(employee_id)
        last_attendance_id = employee.last_attendance_id
        attendance_state = employee.attendance_state
        last_check_in = employee.last_check_in 
        last_check_out = employee.last_check_out


    @validate_token
    @http.route("/api/hr/v1.0/checkin", type="http", auth="none", methods=["POST"], csrf=False)
    def attendance_checkin(self, **post):
        employee_id = int(post['employee_id'])
        employee = request.env['hr.employee'].browse(employee_id)
        _logger.info(employee)
        _logger.info(employee.attendance_state)
        if employee.attendance_state == 'checked_out':
            hr_attendance_id = request.env['hr.attendance'].create({
                'employee_id': employee_id,
                'check_in': datetime.now(),
            })
            return valid_response({},200)
        else:
            return invalid_response("error")

    @validate_token
    @http.route("/api/hr/v1.0/checkout", type="http", auth="none", methods=["POST"], csrf=False)
    def attendance_checkout(self, **post):
        employee_id = int(post['employee_id'])
        employee = request.env['hr.employee'].browse(employee_id)
        _logger.info(employee.attendance_state)
        _logger.info(employee.last_attendance_id)
        if employee.attendance_state == 'checked_in':
            current_date =  employee.last_attendance_id.check_in.date() 
            if current_date == date.today():
                employee.last_attendance_id.write({'check_out': datetime.now()})
                return valid_response({},200)
            else:
                return invalid_response("error","Date not match")
        else:
            return invalid_response("error", "Employee not checkin yet")
