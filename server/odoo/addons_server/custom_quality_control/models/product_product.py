
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.product_line",
        inverse_name="product",
        string="Quality control triggers",
    )
