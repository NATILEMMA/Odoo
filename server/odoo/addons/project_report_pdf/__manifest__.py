
{
    'name': 'Project Report XLS & PDF',
    'version': '13.0.1.0.0',
    "category": "Project",
    'author': '',
    'website': "",
    'maintainer': '',
    'company': '',
    'summary': """Advanced PDF & XLS Reports for Project With Filtrations""",
    'description': """Advanced PDF & XLS Reports for Project With Filtrations, Odoo 13, Odoo13""",
    'depends': ['base', 'project'],
    'license': 'AGPL-3',
    'data': ['views/action_manager.xml',
             'wizard/project_report_wizard_view.xml',
             'report/project_report_pdf_view.xml',
             'views/project_report_button.xml',
             'views/project_report.xml'
             ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
