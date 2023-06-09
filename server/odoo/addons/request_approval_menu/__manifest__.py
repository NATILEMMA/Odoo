{
    'name': "menu category",
    'version': '13.0.1.0.0',
    'summary': """Manage Visitor Gate Operations:Visitors, Devices Carrying Register, Actions""",
    'description': """Helps You To Manage Visitor Gate Operations, Odoo13, Odoo 13""",
    'author': "Amen mesfin",
    'company': "Tria trading plc",
    'website': "http://triaplc.com/",
    'category': 'Industries',
    'depends': ['base', 'hr','hr_expense','hr_disciplinary_tracking','employee_orientation',
                'hr_request_position', 'hr_recruitment_request','hr_disciplinary_tracking','hr_menu_organizer','hr_job_wages',
                'hr_shift_management', 'ohrms_loan','hr_recruitment_request', 'ohrms_salary_advance','stock_transfer'
                ],
    'data': [
        'views/menu.xml',
        'views/hr.xml',
    ],
    'images': ['static/img/emreq.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 0,
}
