from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError, ValidationError


class Product(models.Model):
    _inherit = 'product.product'
    _description = 'Adding is asset field'

    is_coupon = fields.Boolean(string="Is coupon")
    amount_liter = fields.Float(string="liter amount")
