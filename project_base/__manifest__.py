# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Base Core',
    'version': '18.0',
    'category': 'Project Lifecycle Management',
    'author': "",
    'summary': 'Project Base Core',
    'website': '',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_project.xml',
        'wizards/wizard_bulk_create_task_views.xml',
        "data/project_phase_data.xml",
        "security/ir.model.access.csv"
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
