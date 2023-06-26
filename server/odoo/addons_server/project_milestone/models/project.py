
from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    milestone_ids = fields.One2many(
        "project.milestone", "project_id", string="Milestones", copy=True
    )
    use_milestones = fields.Boolean(help="Does this project use milestones?",string="Use Quarters")
