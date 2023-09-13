# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError
import re

class HrEmployeeMedicalExamination(models.Model):

    _name = "hr.employee.medical.examination"
    _description = "Hr Employee Medical Examination"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, track_visibility="onchange", translate=True)

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        readonly=True,
        track_visibility="onchange",
    )

    date = fields.Date(string="Examination Date", track_visibility="onchange",)
    
    result = fields.Selection(
        selection=[("failed", "Failed"), ("passed", "Passed")],
        track_visibility="onchange",
    )

    employee_id = fields.Many2one(
        "hr.employee", string="Employee", required=True, track_visibility="onchange",
    )
    year = fields.Char("Year", default=lambda r: str(datetime.date.today().year), translate=True)
    note = fields.Text(track_visibility="onchange", translate=True)
   

    instution_type_id = fields.Many2one("hr.employee.instution.type", string="Instution Type",)
    instution_id = fields.Many2one("res.partner", string="Instution",)
    examination_type_id = fields.Many2one("hr.employee.medical.examination.type", string="Examination Type",)
    
    
   

    @api.onchange("date")
    def _onchange_date(self):
        for record in self:
            if record.date:
                record.year = str(record.date.year)


    @api.onchange('instution_type_id')
    def onchange_instution_type_id(self):
        for rec in self:
            return {'domain': {'instution_id': [('instution_type_id', '=', rec.instution_type_id.id)]}}
        
    def back_to_draft(self):
        self.write({"state": "draft"})

    def back_to_pending(self):
        self.write({"state": "pending"})

    def to_done(self):

        self.write({"state": "done"})

    def to_cancelled(self):
        self.write({"state": "cancelled"})

    def to_rejected(self):
        self.write({"state": "rejected"})
    
    def to_pending(self):
        self.write({"state": "pending"})
