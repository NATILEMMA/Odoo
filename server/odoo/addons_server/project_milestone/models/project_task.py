
from odoo import api, fields, models

MONTH = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), 
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ]

class ProjectTask(models.Model):
    _inherit = "project.task"

    name = fields.Many2one('planning.goal', store=True )

    milestone_id = fields.Many2one(
        "project.milestone",
        string="Milestone",
        group_expand="_read_group_milestone_ids",
        domain="[('project_id', '=', project_id)]",
    )
    use_milestones = fields.Boolean(
        related="project_id.use_milestones", help="Does this project use milestones?"
    )
    month = fields.Selection(MONTH,
                          string='Month',default="1", store=True,)
    
    @api.model
    def _read_group_milestone_ids(self, milestone_ids, domain, order):
        if "default_project_id" in self.env.context:
            milestone_ids = self.env["project.milestone"].search(
                [("project_id", "=", self.env.context["default_project_id"])]
            )
        return milestone_ids
