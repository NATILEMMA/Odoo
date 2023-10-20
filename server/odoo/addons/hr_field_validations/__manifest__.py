
{
  'name': 'Hr field validation',
  'version': '1.1',
  'description': "",
  'author': 'Natnael Lemma',
  'depends': [
    'base','hr_contract','hr',"hr_payroll_community","oh_employee_documents_expiry","hr_recruitment_request","ohrms_loan","ohrms_salary_advance","hr_job_wages","ohrms_loan_accounting","hr_holidays","hr_expense",
  ],
  'data': [
    'views/res_user_inherit.xml',
    'views/hr_employee.xml',
  ],
  'sequence': 1,
  'category': 'Category',
  'application': True,
  'installable': True,
  'auto-install': False
}
