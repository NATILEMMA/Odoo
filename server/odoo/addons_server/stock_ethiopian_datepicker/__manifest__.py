
{
    "name": "Inventory Ethiopian Datepicker",
    "summary": "Ethiopian Calendar"
    "company",
    "version": "13.0.1",
    "author": "",
    "website": " ",
    "category": "",
    "depends": ["stock",'stock_account','account','stock_card_report'],
    "license": "LGPL-3",
    "data": [
        "wizard/inherit_inventory_report_view.xml",
        "views/inherit_stock_picking_view.xml",
        # "views/inherit_planning_tasks.xml",
        # "views/inherit_planning.xml",
        
    ],
      'application': True,

  'installable': True,
  'auto_install': False,
  'sequence': 1001

}
