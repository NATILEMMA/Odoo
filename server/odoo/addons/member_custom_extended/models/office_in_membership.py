from odoo import api, fields, models, _


class Cells(models.Model):
    _inherit = ['member.cells']

    maximum_number_reached = fields.Boolean(compute="_compute_maximum_cell_member")

    @api.depends("members_ids","leagues_ids")
    def _compute_maximum_cell_member(self):

        for rec in self:
            if rec.for_which_members == "member":
        
                cell_config = self.env['cell.configuration'].search([('for_members_or_leagues','=','member')])

                if cell_config and cell_config.maximum_number:
                    
                    members_count = len(rec.members_ids)
                    if cell_config.maximum_number <= members_count:
                        rec.maximum_number_reached = True
                    else:
                        rec.maximum_number_reached = False
                else:
                    rec.maximum_number_reached = False
            else:
                 
                cell_config = self.env['cell.configuration'].search([('for_members_or_leagues','=','league')])

                if cell_config and cell_config.maximum_number:
                  
                    league_count = len(rec.leagues_ids)
                    if cell_config.maximum_number <= league_count :
                        rec.maximum_number_reached = True
                    else:
                        rec.maximum_number_reached = False
                else:         
                    rec.maximum_number_reached = False

    
    def split_cell(self):
        if self.for_which_members == "member":
            return {
                    "name": _(""),
                    "view_mode": "form",
                    "res_model": "cell.split.wizard",
                    "target": "new",
                    "type": "ir.actions.act_window",
                    "context": {
                        "default_cell_name":self.name + " split",
                        "default_subcity_id": self.id,
                        "default_wereda_id": self.wereda_id.id,
                        "default_member_cell_type_id": self.member_cell_type_id.id,
                        "default_cell_id":self.id,
                        "default_for_which_members":self.for_which_members
                },
            }

        else:
             return {
                    "name": _(""),
                    "view_mode": "form",
                    "res_model": "league.cell.split.wizard",
                    "target": "new",
                    "type": "ir.actions.act_window",
                    "context": {
                        "default_subcity_id": self.subcity_id.id,
                        "default_wereda_id": self.wereda_id.id,
                        "default_league_cell_type_id": self.league_cell_type_id,
                        "default_cell_id":self.id,
                        "default_for_which_members":self.for_which_members
                },
            }

            
    