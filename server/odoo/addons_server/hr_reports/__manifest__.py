
{
  'name': 'Hr reports',
  'version': '1.1',
  'description': "This module help to organize several hr related reports in one menu",
  'author': 'Tria -Natnael lemma',
  'depends': [
    'hr','report', 'oh_hr_lawsuit_management','ohrms_salary_advance' ,'hr_employee_medical_examination', 'hr_disciplinary_tracking', 'request_approval_menu', 'stock_transfer'
  ],
    'data': [
             'views/hr_department.xml',
             'views/hr_employee.xml',
             'views/hr_job.xml',
             ],
  'installable': True,
  'auto-install': True
}
