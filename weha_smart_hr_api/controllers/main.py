# -*- coding: utf-8 -*-
#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
import re
import ast
import functools
import logging
import json
import werkzeug.wrappers
from odoo.exceptions import AccessError
from odoo.addons.weha_smart_pos_api.common import invalid_response, valid_response
from odoo import http
from datetime import datetime
from odoo.http import request
import base64

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
        request.env.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap



class HrController(http.Controller):
    
    @validate_token
    @http.route("/api/smarthr/v1.0/checkin", type="http", auth="none", methods=["POST"], csrf=False)
    def checkin(self, **post):
        pass 

    @validate_token
    @http.route("/api/smarthr/v1.0/checkout", type="http", auth="none", methods=["POST"], csrf=False)
    def checkin(self, **post):
        pass 

    @validate_token
    @http.route("/api/smarthr/v1.0/todayatt", type="http", auth="none", methods=["POST"], csrf=False)
    def today_attendant(self, **post):
        pass 
    

    @validate_token
    @http.route("/api/smarthr/v1.0/weekatt", type="http", auth="none", methods=["POST"], csrf=False)
    def week_attendant(self, **post):
        pass 
    
    @validate_token
    @http.route("/api/smarthr/v1.0/monthatt", type="http", auth="none", methods=["POST"], csrf=False)
    def month_attendant(self, **post):
        pass 
    

    