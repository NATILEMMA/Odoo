
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qc_triggers = fields.One2many(
        comodel_name="qc.trigger.product_template_line",
        inverse_name="product_template",
        string="Quality control triggers",
    )
