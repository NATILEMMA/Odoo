# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anusha P P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    'name': "Visits",
    'version': '13.0.1.0.0',
    'summary': """Manage Visitor Gate Operations:Visitors, Devices Carrying Register, Actions""",
    'description': """Helps You To Manage Visitor Gate Operations, Odoo13, Odoo 13""",
    'author': "Tria trading plc",
    'maintainer': 'Bushra Mustofa',
    'company': "Tria trading plc",
    'website': "http://triaplc.com/",
    'category': 'Industries',
    'depends': ['base', 's2u_online_appointment', 'utm'],
    'data': [
        'security/fo_security.xml',
        'security/ir.model.access.csv',
        'data/activity.xml',
        'data/mail_template.xml',
        # 'data/fed_states_ethiopia.xml',
        'views/appointment_slot_view.xml',
        'views/appointment_option_view.xml',
        'views/fo_visit.xml',
        'views/fo_visitor.xml',
        'views/fo_property_counter.xml',
        'views/department_inherit.xml',
        # 'views/fed_states_ethiopia_view.xml',
        'wizard/reschedule.xml',
        'report/report.xml',
        'report/fo_property_label.xml',
        'report/fo_visitor_label.xml',
        'report/visitors_report.xml',
        'report/meeting_minute.xml'
    ],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 0,
}
