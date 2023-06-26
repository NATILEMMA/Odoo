
{
    "name": "Ethiopian Calander Module",
    "summary": "Ethiopian Calander"
    "company",
    "version": "13.0.1",
    "author": "mes",
    "website": " ",
    "category": "",
    "depends": ["calendar","hr_holidays"],
    "license": "LGPL-3",
    "data": [
        'data/data.xml',
        # 'security/calendar_group_rules.xml',
        "views/ethioCalview.xml",
        # 'views/calendar_views.xml',

    ],
      'application': True,
  'qweb': [
        'static/ethiopian_datepicker.xml',
        'static/src/xml/calendar_view.xml'

    ],
  'installable': True,
  'auto_install': False,
  'sequence': 1001

}
