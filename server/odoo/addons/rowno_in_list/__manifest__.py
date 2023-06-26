# -*- encoding: utf-8 -*-
{
    'name': "Row Number in tree or list view",
    'version': '16.0.0.4',
    'author': 'Amen Mesfin',
    'company': 'Tria PLC',
    'website': 'http://www.triaplc.com',
    'summary': 'Display row numbers in tree or list views.',
    'description': """By installing this module, user can see row number in Odoo backend tree view. sequence in list, Numbering List View, row count, row counting, show count list, list view row count, number in row""",
    'category': 'Extra Tools', 
     
    "depends" : ['web'],
    'data': [
             'views/listview_templates.xml',
             ],
    'images': ['static/description/banner.png',
               'static/description/icon.png',],

    'license': 'AGPL-3',
    'email': "support@triaplc.com",
    'qweb': [
            ],  
    
    'installable': True,
    'application'   : True,
    'auto_install'  : False,
}
