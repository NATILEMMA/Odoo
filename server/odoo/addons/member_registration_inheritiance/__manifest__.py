{
  'name':'Membership Custom',
  'version': '1.1',
  'description': 'This will customize odoo',
  'author': 'Tria Trading',
  'depends': [
    'utm',
    'member_registration',
  ],
  'data': [
    'views/assembly_inherit.xml',
    'views/complaint_inherit.xml',
    'views/membership_payment_inherit.xml',
    'views/offices_in_membership_inherit.xml',
    'views/training_inherit.xml',
    'views/transfer_inherit.xml',
    'views/minor_configurations_inherit.xml',
  ],
  # 'category': 'Member/Handlers',
  'application': True,
  'installable': True,
  'auto_install': False,
  'sequence': 1
}
