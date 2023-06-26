# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Asset depreciation report',
    'version': '1.0',
    'author': 'Grupo Tecnoturistico DA S.A.S de C.V.',
    'depends': ['account', 'om_account_asset'],
    'description': 'Get report for depreciated assets',
    'summary': 'Odoo 13 Disposed Assets Management',
    'category': 'Accounting',
    'sequence': 1,
    'license': 'LGPL-3',
    'images': ['static/description/ttda.jpg'],
    'data': [
        'report/template.xml',
        'views/asset_depreciation_report.xml',
    ],
}
