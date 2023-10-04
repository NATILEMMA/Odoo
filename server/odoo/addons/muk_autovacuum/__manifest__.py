{
    'name': 'MuK Autovacuum',
    'summary': 'Configure automatic garbage collection',
    'version': '13.0.3.0.1',
    'category': 'Extra Tools',
    'license': 'LGPL-3',
    'author': 'Tria Trading',
    'depends': [
        'muk_utils',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/rules.xml',
        'data/rules.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
    'auto_install': False,
}