# -*- coding: utf-8 -*-
{
    'name': "Perfomance Evaluation",

    'summary': """
         Extend functioality for performance Evaluation""",

    'description': """
        This will be used for the Employee performance evaluation Program in the system.
    """,

    'author': "Vaibhav",
    'website': "vaibhav14b@gmail.com",
    'images': ["static/description/evaluation_prog.png"],
    'category': 'Human Resources/Employees',
    'version': '14.0.1',
    'license': 'AGPL-3',
    'depends': ['hr', 'base', 'reconciliation', 'web_notify'],
    'data': [
        'security/performance_evaluation_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_activity_type.xml',
        'data/cron_probabtion_date_reminder.xml',
        'views/performance_evaluation_view.xml',
        'views/employee_inherit.xml'
    ],

    'installable': True,
    'application': True,
        
}
