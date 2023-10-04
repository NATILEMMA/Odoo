from odoo import api, fields, models, _
from odoo.exceptions import UserError ,ValidationError


class MemberCellSplitWizard(models.TransientModel):
    _name = "cell.split.wizard"
    _description = "cell split wizard"

    cell_name = fields.Char(required=True, String="New cell name")
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", readonly=True)
    member_cell_type_id = fields.Many2one('membership.organization', readonly=True, string="Organization")
    cell_id = fields.Many2one('member.cells', readonly=True)
    members_ids = fields.Many2many('res.partner', 'member_split_rel',  domain="[('member_sub_responsibility', '!=', 1), ('member_sub_responsibility', '!=', 2), ('member_responsibility', '!=', 2), ('member_cells', '=', cell_id)]", string="Members",)
    leaders_ids = fields.Many2many('res.partner', 'leader_split_rel', domain="['&', '|', '|', ('member_sub_responsibility', '=', 1), ('member_sub_responsibility', '=', 2), ('member_responsibility', '=', 2), ('member_cells', '=', cell_id)]", string="Leaders")
    leagues_ids = fields.Many2many('res.partner', 'league_split_rel',  domain="[('league_sub_responsibility', '!=', 1), ('league_sub_responsibility', '!=', 2), ('league_responsibility', '!=', 32), ('league_member_cells', '=', cell_id)]", string="Leagues")
    league_leaders_ids = fields.Many2many('res.partner', 'league_leader_split_rel', domain="['&', '|', '|', ('league_sub_responsibility', '=', 1), ('league_sub_responsibility', '=', 2), ('league_responsibility', '=', 32), ('league_member_cells', '=', cell_id)]", string="League Leaders")
    members_ids_mixed = fields.Many2many('res.partner', 'member_mixed_split_rel',  domain="[('member_sub_responsibility', '!=', 1), ('member_sub_responsibility', '!=', 2), ('member_responsibility', '!=', 2), ('member_cells', '=', cell_id)]", string="Mixed Members")
    leaders_ids_mixed = fields.Many2many('res.partner', 'leader_mixed_split_rel', domain="['&', '|', '|', ('member_sub_responsibility', '=', 1), ('member_sub_responsibility', '=', 2), ('member_responsibility', '=', 2), ('member_cells', '=', cell_id)]", string="Mixed Leaders")
    leagues_ids_mixed = fields.Many2many('res.partner', 'league_mixed_split_rel',  domain="[('league_sub_responsibility', '!=', 1), ('league_sub_responsibility', '!=', 2), ('league_responsibility', '!=', 32), ('league_member_cells', '=', cell_id)]", string="Mixed Leagues")
    league_leaders_ids_mixed = fields.Many2many('res.partner', 'league_mixed_leader_split_rel', domain="['&', '|', '|', ('league_sub_responsibility', '=', 1), ('league_sub_responsibility', '=', 2), ('league_responsibility', '=', 32), ('league_member_cells', '=', cell_id)]", string="Mixed League Leaders")
    supporter_ids = fields.Many2many('supporter.members', store=True, string="Supporters", domain="[('state', 'not in', ['approved', 'rejected']), ('cell_id', '=', cell_id)]")
    candidate_ids = fields.Many2many('candidate.members', store=True, string="Candidates", domain="[('state', 'not in', ['approved', 'rejected']), ('cell_id', '=', cell_id)]")
    main_office = fields.Many2one('main.office',domain = "[('wereda_id','=',wereda_id), ('member_main_type_id','=',member_cell_type_id)]", required=True, string="Basic Organization")
    for_which_members = fields.Char(readonly=True, string="League or Member")
    is_mixed = fields.Boolean(readonly=True)
   
    

    @api.onchange('main_office')
    def _can_not_add_to_main_office(self):
        """This will check if excess cells are in main office"""
        for record in self:
            if record.main_office:
                user = self.env.user
                total_cells = len(record.main_office.cell_ids.ids)
                config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', record.for_which_members)])
                if config:
                    if total_cells > config.maximum_cell:
                        if config.reject:
                            message="The Added Numbers Of Cells Under This Main Office Is " + str(total_cells) + " Which Is More Than " + str(config.maximum_cell) + " According To The Rule Given."
                            raise ValidationError(_(message))
                        else:
                            message = "The Number Of Cells You Added Is Going To Exceed The Maximum Number of Cells Given In The Rule."
                            user.notify_warning(message, '<h4>Maximum Numbers Of Cells Are Exceeding.</h4>', True)
                else:
                    raise UserError(_("Please Configure The Number of Cells Allowed In A Single Main Office"))


        

    def button_split_cell(self): 
        """This function will split a cell"""
        for rec in self:
            if rec.main_office:
                user = self.env.user
                total_cells = len(rec.main_office.cell_ids.ids)
                config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', rec.main_office.for_which_members)])
                if config:
                    if total_cells > config.maximum_cell:
                        if config.reject:
                            message="The Added Numbers Of Cells Under This Main Office Is " + str(total_cells) + " Which Is More Than " + str(config.maximum_cell) + " According To The Rule Given."
                            raise ValidationError(_(message))
                        else:
                            message = "The Number Of Cells You Added Is Going To Exceed The Maximum Number of Cells Given In The Rule."
                            user.notify_warning(message, '<h4>Maximum Numbers Of Cells Are Exceeding.</h4>', True)
                else:
                    raise UserError(_("Please Configure The Number of Cells Allowed In A Single Main Office"))

            cell_config = self.env['cell.configuration'].search([('for_members_or_leagues', '=', rec.for_which_members)])
            if cell_config :
                if rec.is_mixed:
                    if rec.for_which_members == 'league':
                        league_count = len(rec.leagues_ids_mixed.ids) + len(rec.league_leaders_ids_mixed.ids)
                        if league_count > cell_config.maximum_number:
                            if cell_config.reject:
                                    raise UserError(_("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule."))
                            else:
                                message = _("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule.")
                                title = _("<h4>Maximum Numbers Of Members Are Exceeding.</h4>")
                                self.env.user.notify_warning(message, title, True)

                        new_cell = self.env['member.cells'].create({
                            'name': self.cell_name,
                            'subcity_id': self.cell_id.subcity_id.id,
                            'wereda_id': self.wereda_id.id,
                            'member_cell_type_id': self.member_cell_type_id.id,
                            'for_which_members': self.cell_id.for_which_members,
                            'main_office': self.main_office.id,
                            'main_office_mixed': self.main_office.id,
                            'leagues_ids_mixed': [(6, 0, self.leagues_ids_mixed.ids)],
                            'league_leaders_ids_mixed': [(6, 0, self.league_leaders_ids_mixed.ids)],
                            'leagues_ids': [(6, 0, self.leagues_ids_mixed.ids)],
                            'league_leaders_ids': [(6, 0, self.league_leaders_ids_mixed.ids)],
                            'leagues_ids': [(6, 0, self.leagues_ids_mixed.ids)],
                            'league_leaders_ids': [(6, 0, self.league_leaders_ids_mixed.ids)],
                            'supporter_ids': [(6, 0, self.supporter_ids.ids)],
                            'candidate_ids': [(6, 0, self.candidate_ids.ids)]
                        })

                        if league_count < cell_config.minimum_number:                
                            new_cell.write({
                                'state': 'draft',
                                'activate_cell': False,
                            })
                        else:
                            new_cell.write({
                                'state': 'active',
                                'activate_cell': True,
                            })

                        for member in rec.cell_id.leagues_ids_mixed:
                            if member in new_cell.leagues_ids_mixed:
                                rec.cell_id.leagues_ids_mixed = [(3, member.id)]
                                rec.cell_id.leagues_ids = [(3, member.id)]
                                member.write({
                                    'league_member_cells': new_cell.id,
                                    'league_main_office': rec.main_office.id
                                })

                        for member in rec.cell_id.league_leaders_ids_mixed:
                            if member in new_cell.league_leaders_ids_mixed:
                                rec.cell_id.league_leaders_ids_mixed = [(3, member.id)]
                                rec.cell_id.league_leaders_ids = [(3, member.id)]
                                member.write({
                                    'league_member_cells': new_cell.id,
                                    'league_main_office': rec.main_office.id
                                })

                        for supporter in rec.cell_id.supporter_ids:
                            if supporter in new_cell.supporter_ids:
                                rec.cell_id.supporter_ids = [(3, supporter.id)]
                                supporter.write({
                                    'main_office_id': rec.main_office.id,
                                    'cell_id': new_cell.id,
                                })

                        for candidate in rec.cell_id.candidate_ids:
                            if candidate in new_cell.candidate_ids:
                                rec.cell_id.candidate_ids = [(3, candidate.id)]
                                candidate.write({
                                    'main_office_id': rec.main_office.id,
                                    'cell_id': new_cell.id,
                                })

                        league_count = len(rec.cell_id.leagues_ids_mixed.ids) + len(rec.cell_id.league_leaders_ids_mixed.ids)
                        if league_count < cell_config.minimum_number:                
                            rec.cell_id.write({
                                'state': 'draft',
                                'activate_cell': False,
                            })
                        else:
                            rec.cell_id.write({
                                'state': 'active',
                                'activate_cell': True,
                            })

                        return {
                            "name": new_cell.name,
                            "view_mode": "form",
                            "res_model": "member.cells",
                            "res_id": new_cell.id,
                            "target": "current",
                            "type": "ir.actions.act_window",
                        }

                    if rec.for_which_members == 'member':

                        members_count = len(rec.members_ids_mixed.ids) + len(rec.leaders_ids_mixed.ids)
                        if members_count > cell_config.maximum_number:
                            if cell_config.reject:
                                    raise UserError(_("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule."))
                            else:
                                message = _("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule.")
                                title = _("<h4>Maximum Numbers Of Members Are Exceeding.</h4>")
                                self.env.user.notify_warning(message, title, True)

                        new_cell = self.env['member.cells'].create({
                            'name': self.cell_name,
                            'subcity_id': self.cell_id.subcity_id.id,
                            'wereda_id': self.wereda_id.id,
                            'member_cell_type_id': self.member_cell_type_id.id,
                            'for_which_members': self.cell_id.for_which_members,
                            'main_office': self.main_office.id,
                            'main_office_mixed': self.main_office.id,
                            'members_ids_mixed': [(6, 0, self.members_ids_mixed.ids)],
                            'leaders_ids_mixed': [(6, 0, self.leaders_ids_mixed.ids)],
                            'members_ids': [(6, 0, self.members_ids_mixed.ids)],
                            'leaders_ids': [(6, 0, self.leaders_ids_mixed.ids)],
                            'members_ids': [(6, 0, self.members_ids_mixed.ids)],
                            'leaders_ids': [(6, 0, self.leaders_ids_mixed.ids)],
                            'supporter_ids': [(6, 0, self.supporter_ids.ids)],
                            'candidate_ids': [(6, 0, self.candidate_ids.ids)],
                        })

                        if members_count < cell_config.minimum_number:  
                            new_cell.write({
                                'state': 'draft',
                                'activate_cell': False,
                            })            
                        else:
                            new_cell.write({
                                'state': 'active',
                                'activate_cell': True,
                            })  

                        for member in rec.cell_id.members_ids_mixed:
                            if member in new_cell.members_ids_mixed:
                                rec.cell_id.members_ids_mixed = [(3, member.id)]
                                rec.cell_id.members_ids = [(3, member.id)]
                                member.write({
                                    'member_cells': new_cell.id,
                                    'main_office': rec.main_office.id
                                })

                        for member in rec.cell_id.leaders_ids_mixed:
                            if member in new_cell.leaders_ids_mixed:
                                rec.cell_id.leaders_ids_mixed = [(3, member.id)]
                                rec.cell_id.leaders_ids = [(3, member.id)]
                                member.write({
                                    'member_cells': new_cell.id,
                                    'main_office': rec.main_office.id
                                })

                        for supporter in rec.cell_id.supporter_ids:
                            if supporter in new_cell.supporter_ids:
                                rec.cell_id.supporter_ids = [(3, supporter.id)]
                                supporter.write({
                                    'main_office_id': rec.main_office.id,
                                    'cell_id': new_cell.id,
                                })

                        for candidate in rec.cell_id.candidate_ids:
                            if candidate in new_cell.candidate_ids:
                                rec.cell_id.candidate_ids = [(3, candidate.id)]
                                candidate.write({
                                    'main_office_id': rec.main_office.id,
                                    'cell_id': new_cell.id,
                                })

                        members_count = len(rec.members_ids_mixed.ids) + len(rec.leaders_ids_mixed.ids)
                        if members_count < cell_config.minimum_number:                
                            rec.cell_id.write({
                                'state': 'draft',
                                'activate_cell': False,
                            })
                        else:
                            rec.cell_id.write({
                                'state': 'active',
                                'activate_cell': True,
                            })


                        return {
                            "name": new_cell.name,
                            "view_mode": "form",
                            "res_model": "member.cells",
                            "res_id": new_cell.id,
                            "target": "current",
                            "type": "ir.actions.act_window",
                        }
                else:
                    if rec.for_which_members == 'league':
                        league_count = len(rec.leagues_ids.ids) + len(rec.league_leaders_ids.ids)
                        if league_count > cell_config.maximum_number:
                            if cell_config.reject:
                                    raise UserError(_("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule."))
                            else:
                                message = _("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule.")
                                title = _("<h4>Maximum Numbers Of Members Are Exceeding.</h4>")
                                self.env.user.notify_warning(message, title, True)

                        new_cell = self.env['member.cells'].create({
                            'name': self.cell_name,
                            'subcity_id': self.cell_id.subcity_id.id,
                            'wereda_id': self.wereda_id.id,
                            'member_cell_type_id': self.member_cell_type_id.id,
                            'for_which_members': self.cell_id.for_which_members,
                            'main_office': self.main_office.id,
                            'leagues_ids': [(6, 0, self.leagues_ids.ids)],
                            'league_leaders_ids': [(6, 0, self.league_leaders_ids.ids)],
                            'supporter_ids': [(6, 0, self.supporter_ids.ids)],
                            'candidate_ids': [(6, 0, self.candidate_ids.ids)]
                        })

                        if league_count < cell_config.minimum_number:                
                            new_cell.write({
                                'state': 'draft',
                                'activate_cell': False,
                            })
                        else:
                            new_cell.write({
                                'state': 'active',
                                'activate_cell': True,
                            })

                        for member in rec.cell_id.leagues_ids:
                            if member in new_cell.leagues_ids:
                                rec.cell_id.leagues_ids = [(3, member.id)]
                                member.write({
                                    'league_member_cells': new_cell.id,
                                    'league_main_office': rec.main_office.id
                                })

                        for member in rec.cell_id.league_leaders_ids:
                            if member in new_cell.league_leaders_ids:
                                rec.cell_id.league_leaders_ids = [(3, member.id)]
                                member.write({
                                    'league_member_cells': new_cell.id,
                                    'league_main_office': rec.main_office.id
                                })

                        for supporter in rec.cell_id.supporter_ids:
                            if supporter in new_cell.supporter_ids:
                                rec.cell_id.supporter_ids = [(3, supporter.id)]
                                supporter.write({
                                    'main_office_id': rec.main_office.id,
                                    'cell_id': new_cell.id,
                                })

                        for candidate in rec.cell_id.candidate_ids:
                            if candidate in new_cell.candidate_ids:
                                rec.cell_id.candidate_ids = [(3, candidate.id)]
                                candidate.write({
                                    'main_office_id': rec.main_office.id,
                                    'cell_id': new_cell.id,
                                })

                        league_count = len(rec.cell_id.leagues_ids.ids) + len(rec.cell_id.league_leaders_ids.ids)
                        if league_count < cell_config.minimum_number:                
                            rec.cell_id.write({
                                'state': 'draft',
                                'activate_cell': False,
                            })
                        else:
                            rec.cell_id.write({
                                'state': 'active',
                                'activate_cell': True,
                            })

                        return {
                            "name": new_cell.name,
                            "view_mode": "form",
                            "res_model": "member.cells",
                            "res_id": new_cell.id,
                            "target": "current",
                            "type": "ir.actions.act_window",
                        }

                    if rec.for_which_members == 'member':

                        members_count = len(rec.members_ids.ids) + len(rec.leaders_ids.ids)
                        if members_count > cell_config.maximum_number:
                            if cell_config.reject:
                                    raise UserError(_("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule."))
                            else:
                                message = _("The Number Of Members Added Is Going To Exceed The Maximum Number Given In The Rule.")
                                title = _("<h4>Maximum Numbers Of Members Are Exceeding.</h4>")
                                self.env.user.notify_warning(message, title, True)

                        new_cell = self.env['member.cells'].create({
                            'name': self.cell_name,
                            'subcity_id': self.cell_id.subcity_id.id,
                            'wereda_id': self.wereda_id.id,
                            'member_cell_type_id': self.member_cell_type_id.id,
                            'for_which_members': self.cell_id.for_which_members,
                            'main_office': self.main_office.id,
                            'members_ids': [(6, 0, self.members_ids.ids)],
                            'leaders_ids': [(6, 0, self.leaders_ids.ids)],
                            'supporter_ids': [(6, 0, self.supporter_ids.ids)],
                            'candidate_ids': [(6, 0, self.candidate_ids.ids)],
                        })

                        if members_count < cell_config.minimum_number:  
                            new_cell.write({
                                'state': 'draft',
                                'activate_cell': False,
                            })            
                        else:
                            new_cell.write({
                                'state': 'active',
                                'activate_cell': True,
                            })  

                        for member in rec.cell_id.members_ids:
                            if member in new_cell.members_ids:
                                rec.cell_id.members_ids = [(3, member.id)]
                                member.write({
                                    'member_cells': new_cell.id,
                                    'main_office': rec.main_office.id
                                })

                        for member in rec.cell_id.leaders_ids:
                            if member in new_cell.leaders_ids:
                                rec.cell_id.leaders_ids = [(3, member.id)]
                                member.write({
                                    'member_cells': new_cell.id,
                                    'main_office': rec.main_office.id
                                })

                        for supporter in rec.cell_id.supporter_ids:
                            if supporter in new_cell.supporter_ids:
                                rec.cell_id.supporter_ids = [(3, supporter.id)]
                                supporter.write({
                                    'main_office_id': rec.main_office.id,
                                    'cell_id': new_cell.id,
                                })

                        for candidate in rec.cell_id.candidate_ids:
                            if candidate in new_cell.candidate_ids:
                                rec.cell_id.candidate_ids = [(3, candidate.id)]
                                candidate.write({
                                    'main_office_id': rec.main_office.id,
                                    'cell_id': new_cell.id,
                                })

                        members_count = len(rec.members_ids.ids) + len(rec.leaders_ids.ids)
                        if members_count < cell_config.minimum_number:                
                            rec.cell_id.write({
                                'state': 'draft',
                                'activate_cell': False,
                            })
                        else:
                            rec.cell_id.write({
                                'state': 'active',
                                'activate_cell': True,
                            })


                        return {
                            "name": new_cell.name,
                            "view_mode": "form",
                            "res_model": "member.cells",
                            "res_id": new_cell.id,
                            "target": "current",
                            "type": "ir.actions.act_window",
                        }
            else:
                raise UserError(_("Please Configure The Number of Members Allowed In A Single Cell"))
        