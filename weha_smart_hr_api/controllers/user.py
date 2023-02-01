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
from odoo import http
from odoo.http import request

from datetime import datetime
import json
import werkzeug
import logging

_logger = logging.getLogger(__name__)

class QueuePickup(http.Controller):

    @http.route('/queue/pickup/listall', auth='public')
    def category_list(self, **kw):
        env_type = http.request.env['smart.hospital.queue.pickup']
        args = [('state', '=', 'open')]
        type_ids = env_type.sudo().search_read(args)
        return json.dumps(type_ids)
