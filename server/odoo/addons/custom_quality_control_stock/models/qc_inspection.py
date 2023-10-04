
from odoo import api, fields, models
from odoo.fields import first
import logging
_logger = logging.getLogger(__name__)

class QcInspection(models.Model):
    _inherit = "qc.inspection"

    picking_id = fields.Many2one(
        comodel_name="stock.picking", compute="_compute_picking", store=True
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", compute="_compute_lot", store=True
    )

    lot_ids = fields.Many2many("stock.production.lot", compute="_compute_lot_ids", store=True
    )


    def object_selection_values(self):
        result = super().object_selection_values()
        result.extend(
            [
                ("stock.picking", "Picking List"),
                ("stock.move", "Stock Move"),
                ("stock.production.lot", "Lot/Serial Number"),
            ]
        )
        return result

    @api.depends("object_id")
    def _compute_picking(self):
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == "stock.move":
                    inspection.picking_id = inspection.object_id.picking_id
                elif inspection.object_id._name == "stock.picking":
                    inspection.picking_id = inspection.object_id
                elif inspection.object_id._name == "stock.move.line":
                    inspection.picking_id = inspection.object_id.picking_id

    @api.depends("object_id")
    def _compute_lot(self):
        _logger.info("#######_compute_lot#### ")
        moves = self.filtered(
            lambda i: i.object_id and i.object_id._name == "stock.move"
        ).mapped("object_id")


        move_lines = self.env["stock.move.line"].search(
            [("lot_id", "!=", False), ("move_id", "in", [move.id for move in moves])]
        )
    
        for inspection in self:
            if inspection.object_id:
                if inspection.object_id._name == "stock.move.line":
                    inspection.lot_id = inspection.object_id.lot_id
                elif inspection.object_id._name == "stock.move":
                    inspection.lot_id = first(
                        move_lines.filtered(
                            lambda line: line.move_id == inspection.object_id
                        )
                    ).lot_id
                   

                elif inspection.object_id._name == "stock.production.lot":
                    inspection.lot_id = inspection.object_id



    @api.depends("object_id")
    def _compute_lot_ids(self):
        _logger.info("#######_compute_lot _ids#### ")
        moves = self.filtered(
            lambda i: i.object_id and i.object_id._name == "stock.move"
        ).mapped("object_id")


        move_lines = self.env["stock.move.line"].search(
            [("lot_id", "!=", False), ("move_id", "in", [move.id for move in moves])]
        )
        # _logger.info("#######move_lines#### %s",move_lines)
        lot_ids = []
        for line in move_lines:
            _logger.info("line:%s",line.lot_id.name)
            lot_ids.append(line.lot_id.id)

        _logger.info("lot_ids:%s",lot_ids)
        for inspection in self:
            if inspection.object_id:
                _logger.info("####inspection.object_id %s",inspection.object_id)

                if inspection.object_id._name == "stock.move.line":
                    _logger.info("####stock.move.line ",inspection.object_id.lot_id.name)
                    inspection.lot_ids = inspection.object_id.lot_id
                elif inspection.object_id._name == "stock.move":
                    inspection.lot_ids = [(6,0, lot_ids)]
                    # inspection.lot_id = first(
                    #     move_lines.filtered(
                    #         lambda line: line.move_id == inspection.object_id
                    #     )
                    # ).lot_id
                    _logger.info("####return  %s",inspection.lot_ids)

                elif inspection.object_id._name == "stock.production.lot":
                    inspection.lot_ids = inspection.object_id

    @api.depends("object_id")
    def _compute_product_id(self):
        """Overriden for getting the product from a stock move."""
        super()._compute_product_id()
        for inspection in self.filtered("object_id"):
            if inspection.object_id._name == "stock.move":
                inspection.product_id = inspection.object_id.product_id
            elif inspection.object_id._name == "stock.move.line":
                inspection.product_id = inspection.object_id.product_id
            elif self.object_id._name == "stock.production.lot":
                inspection.product_id = inspection.object_id.product_id

    @api.onchange("object_id")
    def onchange_object_id(self):
        if self.object_id:
            if self.object_id._name == "stock.move":
                self.qty = self.object_id.product_qty
            elif self.object_id._name == "stock.move.line":
                self.qty = self.object_id.product_qty

    def _prepare_inspection_header(self, object_ref, trigger_line):
        res = super()._prepare_inspection_header(object_ref, trigger_line)
        # Fill qty when coming from pack operations
        if object_ref and object_ref._name == "stock.move.line":
            res["qty"] = object_ref.product_qty
        if object_ref and object_ref._name == "stock.move":
            res["qty"] = object_ref.product_uom_qty
        return res


class QcInspectionLine(models.Model):
    _inherit = "qc.inspection.line"

    picking_id = fields.Many2one(
        comodel_name="stock.picking", related="inspection_id.picking_id", store=True
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot", related="inspection_id.lot_id", store=True
    )
