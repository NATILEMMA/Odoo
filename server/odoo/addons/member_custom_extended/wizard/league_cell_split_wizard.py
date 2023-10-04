from odoo import api, fields, models , _
from odoo.exceptions import UserError,ValidationError



class LeagueCellSplitWizard(models.TransientModel):
    _name = "league.cell.split.wizard"
    _description = "league cell split wizard"
   


    cell_name = fields.Char(required=True,String="New cell name")
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda",readonly=True)
    cell_id = fields.Many2one('member.cells',readonly=True, string="Cell")
    for_which_members = fields.Char(readonly=True,  string="League or Member")
    league_cell_type_id = fields.Char(readonly=True, string="Organization")
    main_office_league = fields.Many2one('main.office', string='League Basic Organization', domain="[('wereda_id','=',wereda_id),('league_main_type_id','=',league_cell_type_id)]" ,required=True)
    leagues_ids = fields.Many2many('res.partner', domain="[('league_member_cells','=',cell_id)]", string="Leagues")
    
    @api.onchange('main_office_league')
    def _can_not_add_to_main_office_league(self):
        """This will check if excess cells are in main office"""
        for record in self:
            if record.main_office_league:
                user = self.env.user
                total_cells = len(record.main_office_league.league_cell_ids.ids)
                config = self.env['main.office.configuration'].search([('for_members_or_leagues', '=', record.for_which_members)])
                if config:
                    if total_cells > config.maximum_cell:
                        if config.reject:
                            message="The Added Numbers Of Cells Under This Main Office Is " + str(total_cells) + " Which Is More Than " + str(config.maximum_cell) + " According To The Rule Given."
                            raise ValidationError(_(message))
                        else:
                            message = "The Number Of Cells You Added Is Going To Exceed The Maximum Number of Cells Given In The Rule."
                            user.notify_warning(message, '<h4>Maximum Numbers Of Members Are Exceeding.</h4>', True)    
                else:
                    raise UserError(_("Please Configure The Number of Cells Allowed In A Single Main Office"))


    def button_split_cell(self): 
            cell_config = self.env['cell.configuration'].search([('for_members_or_leagues','=','league')])
            if cell_config :
                for rec in self:
                    members_count = len(rec.leagues_ids)
                    if cell_config.minimum_number > members_count :
                        raise UserError(("The cell contain less than what is required of "+str(cell_config.minimum_number) + " .Please add more leagues members." )) 
                    
                    elif cell_config.maximum_number < members_count and cell_config.reject  :
                        raise UserError(("The cell contain more than what is required of "+str(cell_config.maximum_number) + " .Please remove leagues members." )) 
                    cell = False
                    for rec in self:
                        cell = rec.cell_id

                
                    diff = len(cell.leagues_ids) - len(rec.leagues_ids)
                    if cell_config.minimum_number > diff :
                            raise UserError(("The orginal cell will contain less than what is required of "+str(cell_config.minimum_number) + " .Please remove leagues members from above list" )) 
                
                        
                    new_cell = self.env['member.cells'].create({
                        'name': self.cell_name,
                        'subcity_id': cell.subcity_id.id,
                        'wereda_id': self.wereda_id.id,
                        'league_cell_type_id': self.league_cell_type_id,
                        'for_which_members': cell.for_which_members,
                        'main_office_league': self.main_office_league.id,
                        'leagues_ids': [(6, 0, self.leagues_ids.ids)],
                        
                    })

                    self.cell_id = new_cell.id

                    new_cell_leagues = [x.name for x in self.leagues_ids]
                    

                    for record in cell.members_ids:
                        # check if the name exists in old cell
                        if record.name in new_cell_leagues:
                            # remove the record from old cell
                            
                            cell.write({
                                        'leagues_ids': [(3, record.id, False)]
                                        })

                    return {
                        "name": new_cell.name,
                        "view_mode": "form",
                        "res_model": "member.cells",
                        "res_id": new_cell.id,
                        "target": "current",
                        "type": "ir.actions.act_window",
                    }
            
                
