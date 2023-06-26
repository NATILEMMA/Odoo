
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    auto_create_lot = fields.Boolean(string="Auto Create Lot")
