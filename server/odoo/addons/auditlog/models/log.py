# Copyright 2015 ABF OSIELL <https://osiell.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AuditlogLog(models.Model):
    _name = "auditlog.log"
    _description = "Auditlog - Log"
    _order = "create_date desc"

    name = fields.Char("Resource Name", size=64, translate=True)
    model_id = fields.Many2one("ir.model", string="Model")
    res_id = fields.Integer("Resource ID")
    user_id = fields.Many2one("res.users", string="User")
    method = fields.Char(size=64, translate=True)
    line_ids = fields.One2many("auditlog.log.line", "log_id", string="Fields updated")
    http_session_id = fields.Many2one("auditlog.http.session", string="Session")
    http_request_id = fields.Many2one("auditlog.http.request", string="HTTP Request")
    log_type = fields.Selection(
        [("full", "Full log"), ("fast", "Fast log")], string="Type"
    )


class AuditlogLogLine(models.Model):
    _name = "auditlog.log.line"
    _description = "Auditlog - Log details (fields updated)"

    field_id = fields.Many2one(
        "ir.model.fields", ondelete="cascade", string="Field", required=True
    )
    log_id = fields.Many2one(
        "auditlog.log", string="Log", ondelete="cascade", index=True
    )
    old_value = fields.Text(translate=True)
    new_value = fields.Text(translate=True)
    old_value_text = fields.Text("Old value Text", translate=True)
    new_value_text = fields.Text("New value Text", translate=True)
    field_name = fields.Char("Technical name", related="field_id.name", translate=True)
    field_description = fields.Char("Description", related="field_id.field_description", translate=True)
