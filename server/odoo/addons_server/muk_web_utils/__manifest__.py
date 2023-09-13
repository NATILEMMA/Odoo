{ 
    "name": "MuK Web Utils",
    "summary": """Utility Features""",
    "version": "13.0.1.0.1", 
    "category": "Extra Tools",
    "license": "LGPL-3",
    "author": "MuK IT",
    "website": "http://www.mukit.at",
    'live_test_url': 'https://mukit.at/r/SgN',
    "contributors": [
        "Mathias Markl <mathias.markl@mukit.at>",
        "Benedikt Jilek <benedikt.jilek@mukit.at>",
    ],
    "depends": [
        "web_editor",
        "muk_autovacuum",
    ],
    "data": [
        "template/assets.xml",
        "views/res_config_settings_view.xml",
        "data/autovacuum.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png'
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "application": False,
    "installable": True,
    'auto_install': False,
} 
