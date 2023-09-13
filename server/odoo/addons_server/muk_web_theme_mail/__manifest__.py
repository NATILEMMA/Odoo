{
    "name": "MuK Backend Theme Mail", 
    "summary": "Backend Theme Mail",
    "version": "13.0.1.0.0",
    'category': 'Extra Tools',
    "license": "LGPL-3",
    "author": "Tria Treading",
    "depends": [
        "mail",
        "muk_web_theme",
    ],
    "data": [
        "template/assets.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png',
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
    'auto_install': True,
}