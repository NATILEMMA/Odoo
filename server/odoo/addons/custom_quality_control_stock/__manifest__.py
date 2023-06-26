{
    "name": "Quality control - Stock",
    "version": "13.0.1.0.1",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "Tria Trading PLC",
    "website": "Tria",
    "depends": ["custom_quality_control", "stock","purchase"],
    "data": [
        "security/ir.model.access.csv",
        "views/qc_inspection_view.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_view.xml",
        "views/stock_production_lot_view.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": True,
}
