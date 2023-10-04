from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class Picking(models.Model):
    _inherit = "stock.picking"

    def action_done(self):
        if self.group_id:
            for order_line in self.move_ids_without_package:
                if order_line.product_id.is_coupon:
                    order_line.product_id.amount_liter = order_line.product_id.amount_liter + order_line.quantity_done
        return super(Picking, self).action_done()





