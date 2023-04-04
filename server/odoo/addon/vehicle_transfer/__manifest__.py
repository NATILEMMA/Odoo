{
    'name': 'Vehicle Transfer',
    'summary': """Manage Vehicle Transfer""",
       'category': "Generic Modules/Human Resources",
    'depends': ['base', 'hr', 'fleet','hr_fleet'],
    'data': [
        'data/data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/employee_fleet_view.xml',
    ],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
