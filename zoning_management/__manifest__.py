# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Zoning Management',
    'version': '18.0',
    'category': 'Project Lifecycle Management',
    'author': "",
    'summary': 'Project Base Custom',
    'website': '',
    'depends': [
        'project','project_base'
    ],
    'data': [
        "wizards/wizard_zoning_task_view.xml",
        "views/project_zoning_analysis_line.xml",
        "reports/zoning_analysis_report.xml",
        "views/project_project.xml",
        "views/project_task.xml",
        "views/project_zoning_analysis.xml",
        "views/menu_items.xml",
        "security/ir.model.access.csv"
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
