{
    'name': 'Payroll Email/Mass E-mail',
    'description': 'Send payslip through Email.',
    'category': 'Generic Modules/Human Resources',
    'depends': ['base', 'hr_payroll_community', 'mail'],
    'data': [
        # 'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/hr_payroll.xml',
        'views/hr_payslip_wizard_view.xml',
        'views/hr_mass_payroll_wizard.xml'
        
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
