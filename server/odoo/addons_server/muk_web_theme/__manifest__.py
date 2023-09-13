{
    "name": "MuK Backend Theme", 
    "summary": "Odoo Community Backend Theme",
    "version": "13.0.1.0.6", 
    "category": "Themes/Backend", 
    "license": "LGPL-3", 
    "author": "Tria Treading",
    "depends": [
        "muk_web_utils",
    ],
    "excludes": [
        "web_enterprise",
    ],
    "data": [
        "template/assets.xml",
        "template/web.xml",
        "views/res_users.xml",
        "views/res_config_settings_view.xml",
        "data/res_company.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "images": [
        'static/description/banner.png',
        'static/description/theme_screenshot.png'
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "application": False,
    "installable": True,
    "auto_install": False,
    "uninstall_hook": "_uninstall_reset_changes",
}
