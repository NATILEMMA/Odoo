
{
    "name": "Ethiopian Calendar for hr",
    "summary": "Ethiopian Calendar"
    "company",
    "version": "13.0.1",
    "author": "Natnael lemma",
    "website": " ",
    "category": "",
    "depends": ["hr","hr_contract","oh_hr_lawsuit_management","hr_employee_medical_examination","stock_transfer","hr_timesheet","hr_expense",],
    "license": "LGPL-3",
    "data": [
        "views/inherit_view.xml",
        "views/inherit_view_hr_employee.xml",
        "views/inherit_view_hr_document.xml",
        "views/inherit_view_hr_lawsuit.xml",
        "views/inherit_view_hr_medical_examination.xml",
        # "views/inherit_view_stock_transfer.xml",
        # "views/hr_timesheet_line_tree.xml",
        # "views/inherit_view_performance_evaluation_program_view_form.xml",
        
        
    ],
      'application': True,

  'installable': True,
  'auto_install': False,
  'sequence': 1001

}
