# ++++++++++++++++++++++++++++++++++++++++++++
{
    'name': 'Fleet Services',
    'version': '1.1',
    'summary': 'Fleet Services',
    'description': """ 
            """,
    'depends': ['hr_expense', 'fleet', 'fleet_operations'],
    'category': 'Extra',
    'sequence': 1,
    'data': [
        'views/menus.xml',
        'views/purchase_order_line.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': True,
    'application': True
}
