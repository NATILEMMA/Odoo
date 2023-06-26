# -*- coding: utf-8 -*-
{
    'name': "Hr Expire Module",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr','hr_payroll_community'],

    # always loaded
    'data': [
        'data/cron.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/hr_contract_views.xml',
        'views/hr_employee_view.xml',
        'views/templates.xml',
        'report/report.xml',
        'report/bank_report_template.xml',
    ],
    # only loaded in demonstration mode
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
