# -*- coding: utf-8 -*-
{
    'name': "Hr Batch Report",
    'version': '0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll_community'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'report/batch_report_template.xml',
        'wizard/bank_report_view.xml'
    ],
    # 'qweb': [
    #    'static/src/tree_button.xml',
    #  ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
