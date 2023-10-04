{
    'name': 'Salary Summary',
    'version': '13.0.1.0.0',
    'summary': 'Handles Salary Summary',
    'depends': ['hr_payroll_community', 'mail'],
    'category': 'Generic Modules/Human Resources',
    'demo': ['data/demo_data.xml'],
    'data': [
        'security/ir.model.access.csv',
        'views/salary_summary.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}

