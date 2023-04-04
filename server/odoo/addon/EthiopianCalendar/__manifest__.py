
{
    "name": "Ethiopian DatePicker",
    "summary": "Ethiopian DatePicker"
    "company",
    "version": "13.0.1",
    "author": "mes",
    "website": " ",
    "category": "",
    "depends": ["contacts","base","calendar",'reconciliation'],
    
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',
        'security/datepicker_group_rules.xml',
        "views/assets.xml",
        "views/view.xml",
        "views/inherit_view.xml"
    ],
      'application': True,
  'qweb': [
        'static/ethiopian_datepicker.xml'
    ],
  'pre_init_hook': 'init',
  'installable': True,
  'auto_install': False,
  'sequence': 1001,

}
