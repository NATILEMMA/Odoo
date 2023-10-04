{
  'name':'Member Custom Annual Planning and Handlers',
  'version': '1.1',
  'description': 'This will customize odoo',
  'author': 'Tria Trading',
  'depends': [
    'utm',
    'member_minor_configuration',
    'report',
  ],
  'data': [
    'security/ir.model.access.csv',
    'data/activity_type.xml',
    'data/auto_remainder.xml',
    'views/annual_plan_history.xml',
    'views/membership_handlers_views.xml',
    'views/cell_meeting.xml',
    'views/member_cells_offices.xml',
    'views/report.xml',
    'report/member_report_views.xml',
    'report/member_report.xml',
  ],
  'application': True,
  'installable': True,
  'auto_install': False,
  'sequence': 1
}
