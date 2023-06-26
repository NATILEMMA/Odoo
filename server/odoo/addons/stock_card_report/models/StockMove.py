from odoo import models, api, fields

class StockMove(models.Model):
    _inherit = "stock.move"

    price_unit = fields.Float(
        'Unit Price', help="Technical field used to record the product cost set by the user during a picking confirmation (when costing "
                           "method used is 'average price' or 'real'). Value given in company currency and in product uom.", copy=False,default=0)  # as it's a technical field, we intentionally don't provide the digits attribute
    cost_price = fields.Float(
        'Balance unit Price at time of move', help="This the balance unit price of the product at the time of purchase.", copy=False, default=0)
    
        
    
    

class StockPicking(models.Model):
    _inherit = "stock.picking"

    
    def action_done(self):
        ret = super().action_done()

        for loop in self.move_ids_without_package:
            print("in stock card report","product",loop.product_id.name,"product value",loop.product_id.standard_price,"unite price",loop.cost_price)
            loop.cost_price = loop.product_id.standard_price
            print("stock move ",loop,loop.cost_price)
        
        return ret