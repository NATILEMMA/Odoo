# -*- coding: utf-8 -*-
{
    'name': "Accounting Ethiopian datepicker",
    'author': "Amen mesfin",
    'version': '0.1',
    'sequence': 1,

    'depends': ['account','reconciliation','account_asset_management','account_asset_depreciation'],

    # always loaded
    'data': [
           'views/accouting_date.xml',
           'views/opening.xml',
           'views/closing.xml',
           'views/account_payment.xml',
           'views/depreciation.xml'
    ],
    # only loaded in demonstration mode
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
