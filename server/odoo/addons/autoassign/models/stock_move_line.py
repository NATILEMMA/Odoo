from odoo import models
from odoo.fields import first
import logging
_logger = logging.getLogger(__name__)

class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    def _prepare_auto_lot(self):
        """
        Prepare multi valued lots per line to use multi creation.
        """
        _logger.info("^^^^^^^^^6 self.product_id.id %s",self.product_id.id)
    
        return {"product_id": self.product_id.id, "company_id": self.company_id.id}

    def set_lot_auto(self):
        """
            Create lots using create_multi to avoid too much queries
            As move lines were created by product or by tracked 'serial'
            products, we apply the lot with both different approaches.
        """
        _logger.info("333333333 $$$$$$$$$$$$$ 333333333333")
        values = []
        v =  {"product_id": self.product_id.id, "company_id": self.company_id.id}

        production_lot_obj = self.env["stock.production.lot"]
        lots_by_product = dict()
        for line in self:
            values.append(line.v                                                                                                                                                                                                                                                                                                                                                                                                                                            )

        _logger.info("333333333 line 333333333333 %s",values)
        
        lots = production_lot_obj.create(values)
        _logger.info("333333333 set_lot_auto 333333333333 %s",lots)

        for lot in lots:
            if lot.product_id.id not in lots_by_product:
                lots_by_product[lot.product_id.id] = lot
            else:
                lots_by_product[lot.product_id.id] += lot
        for line in self:
            lot = first(lots_by_product[line.product_id.id])
            line.lot_id = lot
            _logger.info("ggggggggggggg %s",line.lot_id)

            if lot.product_id.tracking == "serial":
                lots_by_product[line.product_id.id] -= lot
                _logger.info("hhhhhhhhhh %s",lots_by_product[line.product_id.id])

