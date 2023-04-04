{
    'name': 'Attendance Integration with Leave and Payroll',
    'version': '13.0.1.1.2',
    'summary': """Integrating Biometric Device (Model: ZKteco uFace 202) With HR Attendance (Face + Thumb) and Intergrating with leave modules and payroll modules""",
    'description': """This module integrates Odoo with the biometric device and with leave and payroll""",
    'category': 'Generic Modules/Human Resources',
    'depends': ['base_setup', 'hr_attendance','hr_zk_attendance',  'hr_contract',
        'hr_holidays',
        'hr_payroll_community',
        'hr_contract_types',],
    'data': [
        'security/access_group_rules.xml',
        'security/ir.model.access.csv',
        'views/view.xml',
        'data/data.xml'

    ],
    'images': ['static/description/images/bio.png'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
