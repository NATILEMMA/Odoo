# -*- coding: utf-8 -*-
# © 2023 Tria Trading PLC)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Tria Mass Editing v13',
    'version': '13.0.1.1.0',
    'author': 'Amen Mesfin '
              'Tria, ',
    'contributors': [
        'Meseret Babulo',
        'Samra Solomon',
        'Natinael Lema'
    ],
    'category': 'Tools',
    'website': 'http://www.triaplc.com',
    'license': 'GPL-3 or any later version',
    'summary': 'Mass Editing (adaptation  v 10.0 to 13.0)',# boris.gra
    # 'uninstall_hook': 'uninstall_hook',# boris.gra
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/mass_editing_view.xml',
        'views/basic_js.xml',# boris.gra
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
