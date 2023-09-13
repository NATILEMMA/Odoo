

{
    'name': 'Datepicker flags',
    'version': '13.21.03.31',
    'author': 'mes',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'sequence': 2,
    'summary': """ 
    """,
    'images': ['static/description/banner.gif'],
    'depends': [
        'base_setup',
        'web',
        'mail',
        'iap',
    ],
    'data': [
        'views/app_odoo_customize_views.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': True,
}
