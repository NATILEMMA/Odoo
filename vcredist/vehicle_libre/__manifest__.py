# ++++++++++++++++++++++++++++++++++++++++++++
{
    'name': 'Vehicle Libre',
    'version': '1.1',
    'summary': 'Vehicle Libre',
    'description': """ 
            """,
    'depends': ['fleet_operations','fleet', 'purchase','vehicle_transfer'],
    'category': 'Extra',
    'sequence': 1,
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'data/activity_type.xml',
        'data/libray_sequence.xml',
        'wizard/libre_update_wizard.xml',
        'views/menus.xml',
        'views/report.xml'

    ],
    'test': [
    ],
    'installable': True,
    'auto_install': True,
    'application': True
}
