from odoo import api , fields , models

class ProductionLot(models.Model):
    _inherit = ['stock.production.lot']

    associated_asset = fields.Many2one("account.asset", "Associated asset",readonly=True)