from odoo import api, fields, models



# from multiprocessing import Process
import logging
_logger = logging.getLogger(__name__)




class stock_picking(models.Model):
    _inherit = "stock.picking"

