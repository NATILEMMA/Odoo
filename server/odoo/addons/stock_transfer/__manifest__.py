# ++++++++++++++++++++++++++++++++++++++++++++
{
    'name': 'Stock Transfer',
    'version': '1.1',
    'summary': 'Stock Transfer Request',
    'description': """ 
            """,
    'depends': ['purchase_request','mail','utm','hr'],
    'category': 'Extra',
    'sequence': 1,
    'data': [
        'views/menus.xml',
        # 'data/ir.cron.data.xml',
        'security/ir.model.access.csv',
        'sequences/sequences.xml',
        'views/stock_picking.xml'
    ],
    'test': [
    ],
    'images': ['static/description/exchange.png'],
    'installable': True,
    'auto_install': True,
    'application': True
}
