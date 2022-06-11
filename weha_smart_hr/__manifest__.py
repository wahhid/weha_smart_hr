# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'WEHA Smart HR',
    'version': '14.0.1.0',
    'category': 'Human Resources/Schedule',
    'sequence': 95,
    'summary': 'WEHA Smart HR',
    'description': "",
    'website': 'https://www.weha-id.com',
    'images': [
    ],
    'depends': [
        'mail',
        'portal',
        'hr',
        'hr_attendance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_param.xml',
        'wizard/weha_hr_schedule_exception_wizard_view.xml',
        'wizard/weha_hr_schedule_attendance_wizard_view.xml',
        'view/res_users_view.xml',
        'view/weha_smart_hr_menu.xml',
        'view/weha_hr_schedule_view.xml',
        "views/weha_smart_hr_portal_template.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [
    ],
    'license': 'LGPL-3',
}