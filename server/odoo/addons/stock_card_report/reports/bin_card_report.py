# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class BinCardView(models.TransientModel):
    _name = "bin.card.view"
    _description = "bin Card View"
    _order = "date"

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product")
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    is_initial = fields.Boolean()
    product_in = fields.Float()
    product_out = fields.Float()
    note = fields.Text()
    uom_id = fields.Many2one(related="product_id.uom_id")
    uom_name = fields.Char(related="uom_id.name")


class BinCardReport(models.TransientModel):
    _name = "report.bin.card.report"
    _description = "bin Card Report"

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    product_ids = fields.Many2many(comodel_name="product.product")
    location_id = fields.Many2one(comodel_name="stock.location")

    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name="bin.card.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"
        self.date_to = self.date_to or fields.Date.context_today(self)
        locations = self.env["stock.location"].search(
            [("id", "child_of", [self.location_id.id])]
        )

        self._cr.execute(
            """
            SELECT move.reference, move.date, move.product_id, move.product_qty,
                move.product_uom_qty, move.product_uom, move.reference,
                move.location_id, move.location_dest_id,
                case when move.location_dest_id in %s
                    then move.product_qty end as product_in,
                case when move.location_id in %s
                    then move.product_qty end as product_out,
                case when move.date < %s then True else False end as is_initial
            FROM stock_move move
            WHERE (move.location_id in %s or move.location_dest_id in %s)
                and move.state = 'done' and move.product_id in %s
                and CAST(move.date AS date) <= %s
            ORDER BY move.date, move.reference
        """,
            (
                tuple(locations.ids),
                tuple(locations.ids),
                date_from,
                tuple(locations.ids),
                tuple(locations.ids),
                tuple(self.product_ids.ids),
                self.date_to,
            ),
        )
        bins_card_results = self._cr.dictfetchall()

        print("**************************************")
        
        ReportLine = self.env["bin.card.view"]

        # getting notes of every transfer from stock.picking as a comment or remark

        for line in bins_card_results:
            stock_picking_record = self.env['stock.picking'].search([('name','=',line['reference'])],limit=1)
            if stock_picking_record.note:
                line.update({'note':stock_picking_record.note})
            else:
                line.update({'note':""})

        self.results = [ReportLine.new(line).id for line in bins_card_results]
        print(self.results)
        for res in self.results:
            print(res.uom_id)
            print(res.uom_name)
        
            
    def _get_initial(self, product_line):
        product_input_qty = sum(product_line.mapped("product_in"))
        product_output_qty = sum(product_line.mapped("product_out"))
        return product_input_qty - product_output_qty

    def print_report(self, report_type="qweb"):
        print("********************************* report type in print report",report_type)
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("stock_card_report.action_bin_card_report_xlsx")
            or self.env.ref("stock_card_report.action_bin_card_report_pdf")
        )
        print("action",action.name)
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "stock_card_report.report_bin_card_report_html"
            ).render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()
