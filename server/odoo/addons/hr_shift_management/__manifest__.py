{
  'name': 'Hr Shift Management',
  'version': '1.1',
  'description': "",
  'depends': [
    'hr',
    'hr_contract'
  ],
  'data': [
      'security/ir.model.access.csv',
      'views/shift_sequence.xml',
      'views/hr_shift_management_views.xml',
      'views/hr_employee_custom.xml',
      'views/hr_employee_shift.xml'
  ],
  'sequence': 1,
  'category': 'Category',
  'application': False,
  'installable': True,
  'auto-install': False
}