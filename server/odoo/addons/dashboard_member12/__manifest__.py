
{
    "name": "Portal Dashboard",
    "summary": "",
    "version": "13.1.0.3",
    "category": "",
    "website": "",
	"description": """
    """,
	'images':[
        'images/f.png'
	],
    "author": "Tria Trading",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        'visitor_gate_management',
        'event',
        'website_event',
    ],
    "data": [
		'views/template.xml',
		'views/add_complain.xml',
		'views/my_complain.xml',
		'views/my_transfers.xml',
		'views/request_transfer.xml',
		'views/add_attachment.xml',
		'views/error_log.xml',
		'views/my_appointments.xml',
		'views/create_appointments.xml',
		'views/change_password.xml',
		'views/events.xml',
		'views/my_payments.xml',
		'views/my_profile.xml',
        'views/reset_password.xml',
		'views/feedback.xml',
        'views/supporter.xml',
		
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
