{
  'name':'Hr Holidays Ethiopian Calendar',
  'version': '1.1',
  'description': 'This will customize hr holidays Calendars',
  'author': 'Tria Trading',
  'depends': [
      'hr_holidays_custom',
      'EthiopianCalendar',
      'hr_holidays',
  ],
  'data': [
      'views/hr_employee_eth_calendar.xml',
      'views/hr_leave_allocation_eth_calendar.xml',
      'views/hr_leave_type_eth_calendar.xml',
      'wizard/hr_leave_request.xml',
  ],
  'installable': True,
  'auto_install': False,
  'sequence': 1
}