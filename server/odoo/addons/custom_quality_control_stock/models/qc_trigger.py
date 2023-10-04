
from odoo import fields, models


class QcTrigger(models.Model):
    _inherit = "qc.trigger"

    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", readonly=True, ondelete="cascade"
    )
