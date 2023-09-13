{
    "name": "MuK Security",
    "summary": """Security Features""",
    "version": "12.0.2.0.1",
    "category": "Extra Tools",
    "license": "LGPL-3",
    "author": "Tria Treading",
    "depends": [
        "muk_utils",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/access_groups.xml",
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
    "auto_install": False,
    "application": False,
    "installable": True,
    "post_load": "_patch_system",
}