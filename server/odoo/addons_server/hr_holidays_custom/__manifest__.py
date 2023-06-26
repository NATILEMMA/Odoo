{
    'name': 'Time Off Custom',
    'version': '2.0',
    'description': 'This Module Will Customize Leave',
    'depends': ['hr_contract', 'hr_holidays', 'web_notify'],
    'data': [
        'data/autoreminder.xml',
        'views/employee_leave_report.xml',
        'views/hr_contract_inherit.xml',
        'views/hr_leave_allocation_view_form_manager_custom.xml'
    ],
    'sequence': 1,
    'category': 'Category',
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 1
}