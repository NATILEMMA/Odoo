
{
  'name': 'Multi company cration restrict',
  'version': '1.1',
  'description': "This module allows only one company to be created after it is installed!",
  'author': 'Natnael Lemma',
  'depends': [
    'base'
  ],
  'data': [
    'security/security.xml',
  ],
  'sequence': 1,
  'category': 'base',
  'application': True,
  'installable': True,
  'auto-install': False
}
