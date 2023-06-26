# -*- coding: utf-8 -*-
{
    'name': "Show Record Metadata",
    'version': '13.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Allow user view record meta data even without developer mode',
    'author': 'Amen Mesfin',
    'support': 'contact@triaplc.com',
    'website': 'http://triaplc.com',
    'license': 'LGPL-3',
    # 'price': '19',
    # 'currency': 'USD',
    'description': """
    Allow user view record meta data even without developer mode
    """,
    'depends': [
        'base',
        'web'
    ],
    'data': [
        'view/template_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'test': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'web_preload': True,
}
