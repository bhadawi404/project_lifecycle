# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project SOP Management',
    'version': '18.0',
    'category': 'Project Lifecycle Management',
    'author': "",
    'summary': 'Project Standart Operation Procedure',
    'website': '',
    'depends': [
        'project',
    ],
    'data': [
        "views/project_task.xml",
        "views/project_sop.xml",
        "security/ir.model.access.csv"
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
