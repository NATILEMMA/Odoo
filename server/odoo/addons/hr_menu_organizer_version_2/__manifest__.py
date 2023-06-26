
{
  'name': 'Hr Menu Organizer version 2',
  'version': '1.1',
  'description': "This module help to organize the employee menu and reduce the dependency between other module menu that lead to inconsistency",
  'author': 'Natnael Lemma',
  'depends': [
    'hr','base','resource'
  ],
    'data': [
             'security/ir.model.access.csv',
             'views/view.xml',
             ],
  'installable': True,
  'auto-install': True
}
