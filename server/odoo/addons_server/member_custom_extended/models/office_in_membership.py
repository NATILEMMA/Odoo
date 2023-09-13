from odoo import api, fields, models, _


class Cells(models.Model):
    _inherit = ['member.cells']

    maximum_number_reached = fields.Boolean(default=True)


    @api.depends("members_ids", "leagues_ids", "leaders_ids", "league_leaders_ids")
    def _compute_maximum_cell_member(self):
        for rec in self:
            if rec.state == 'active':
                if rec.for_which_members == "member":
                    cell_config = self.env['cell.configuration'].search([('for_members_or_leagues','=','member')])
                    if cell_config and cell_config.maximum_number:
                        
                        members_count = len(rec.members_ids.ids) + len(rec.leaders_ids.ids)
                        if cell_config.maximum_number <= members_count:
                            rec.maximum_number_reached = True
                        else:
                            rec.maximum_number_reached = False
                    else:
                        rec.maximum_number_reached = False


                if rec.for_which_members == "league":
                    cell_config = self.env['cell.configuration'].search([('for_members_or_leagues','=','league')])
                    if cell_config and cell_config.maximum_number:
                        league_count = len(rec.leagues_ids.ids)  + len(rec.league_leaders_ids.ids)
                        if cell_config.maximum_number <= league_count:
                            rec.maximum_number_reached = True
                        else:
                            rec.maximum_number_reached = False
                    else:         
                        rec.maximum_number_reached = False
            if rec.state == 'draft':
                raise UserError(_("You Can't Split A Cell That Is Not In Draft State"))


    
    def split_cell(self):
        """This function will create a wizard to split a cell"""
        return {
                "name": _(""),
                "view_mode": "form",
                "res_model": "cell.split.wizard",
                "target": "new",
                "type": "ir.actions.act_window",
                "context": {
                    "default_cell_name": self.name + " split",
                    "default_wereda_id": self.wereda_id.id,
                    "default_member_cell_type_id": self.member_cell_type_id.id,
                    "default_cell_id": self.id,
                    "default_for_which_members": self.for_which_members,
                    "default_main_office": self.main_office.id,
                    "default_is_mixed": self.is_mixed,
            },
        }

            
    