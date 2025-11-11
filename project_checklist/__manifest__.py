# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Checklist',
    'version': '18.0',
    'category': 'Project Lifecycle Management',
    'author': "",
    'summary': 'Project Checklist',
    'website': '',
    'depends': [
        'project','project_base','hr'
    ],
    'data': [
        "views/project_checklist_line_views.xml",
        "views/project_checklist_views.xml",
        "views/menu_items.xml",
        "security/ir.model.access.csv"
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
