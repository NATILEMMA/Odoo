from odoo import models, api, fields

class StockMove(models.Model):
    _inherit = "stock.move"

    price_unit = fields.Float(
        'Unit Price', help="Technical field used to record the product cost set by the user during a picking confirmation (when costing "
                           "method used is 'average price' or 'real'). Value given in company currency and in product uom.", copy=False,default=0)  # as it's a technical field, we intentionally don't provide the digits attribute
    cost_price = fields.Float(
        'Balance unit Price at time of move', help="This the balance unit price of the product at the time of purchase.", copy=False, default=0)
    
    @api.model
    def create(self, vals):
         
        print("************************** before creation",product.standard_price)
        product = self.env['product.product'].search([('id','=',vals['product_id'])])

        move = super(StockMove, self).create(vals)
        print("************************** after creation",product.standard_price)
        return move
    
    
    
        

