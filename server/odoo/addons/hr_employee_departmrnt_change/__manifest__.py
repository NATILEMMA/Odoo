{
    'name': 'Hr Employee Departmrnt Change',
    'summary': """Records The Department Change""",
    'description': 'This module records the department change.',
    'depends': ['base', 'hr','hr_menu_organizer'],
    'data': [
        'security/ir.model.access.csv',
        'views/departmrnt_change_view.xml', 
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}