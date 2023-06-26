
{
    'name': 'Project Tags',
    'version': '13.0.0.0.0',
    'category': 'Projects & Tasks',
    'sequence': 14,
    'summary': 'Status Indicators',
    'description': """
        Project Tags
        ==================
        This module adds Projected end dates and Health Indicators to Tasks/Projects.
    """,
    'author':  '',
    'depends': [
        'project','hr_timesheet',
    ],
    'data': [
        'views/project_views.xml',
        'views/project_status.xml',
            ],
    'demo': [
    ],
     'images': [
        'static/description/icon.png',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
}
