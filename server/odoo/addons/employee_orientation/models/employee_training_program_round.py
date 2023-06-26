from odoo import api, fields, models, _


class TrianingRound(models.Model):

    _name = "employee.training.program.round"
    _description = "rounds of training for employee"


    name = fields.Char(required=True,string="name")

    _sql_constraints = [('unique_name','unique(name)',' A property tag name  name must be unique')]
    _order = "name"