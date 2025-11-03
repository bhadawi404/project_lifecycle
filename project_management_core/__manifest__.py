{
    'name': 'Project Management Core',
    'version': '1.0',
    'summary': 'Project Management Core',
    'description': """
    """,
    'author': 'Ahmad Badawi',
    'category': 'Project Lifecycle',
    'depends': ['project'],
    'data': [
        'data/project_phase_data.xml',
        'data/project_type_data.xml',
        'views/project_template.xml',
        'views/project_sop.xml',
        'views/project_phase.xml',
        'views/project_type_views.xml',
        'views/menu_items.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}