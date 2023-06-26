from odoo import api, fields, models, _
from odoo.exceptions import UserError ,ValidationError


class MemberCellSplitWizard(models.TransientModel):
    _name = "cell.split.wizard"
    _description = "cell split wizard"

    cell_name = fields.Char(required=True,String="New cell name")
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda",readonly=True)
    member_cell_type_id = fields.Many2one('membership.organization',readonly=True)
    cell_id = fields.Many2one('member.cells',readonly=True)
    members_ids = fields.Many2many('res.partner', domain="[('member_cells','=',cell_id)]")
    main_office = fields.Many2one('main.office',domain = "[('wereda_id','=',wereda_id),('member_main_type_id','=',member_cell_type_id)]",required=True)
    for_which_members = fields.Char("league or member",readonly=True)
   
    

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
            cell_config = self.env['cell.configuration'].search([('for_members_or_leagues','=','member')])
            if cell_config :
                for rec in self:
                    members_count = len(rec.members_ids)
                    if cell_config.minimum_number > members_count :
                        raise UserError(("The cell contain less than what is required of "+str(cell_config.minimum_number) + " .Please add more members." )) 
                    
                    elif cell_config.maximum_number < members_count and cell_config.reject :
                        raise UserError(("The cell contain more than what is required of "+str(cell_config.maximum_number) + " .Please remove members." )) 
                    
                    cell = False
                    for rec in self:
                        cell = rec.cell_id

                    diff = len(cell.members_ids) - len(rec.members_ids)
                    if cell_config.minimum_number > diff :
                            raise UserError(("The orginal cell will contain less than what is required of "+str(cell_config.minimum_number) + " .Please remove members from above list" )) 
                
                        
                    new_cell = self.env['member.cells'].create({
                        'name': self.cell_name,
                        'subcity_id': cell.subcity_id.id,
                        'wereda_id': self.wereda_id.id,
                        'member_cell_type_id': self.member_cell_type_id.id,
                        'for_which_members': cell.for_which_members,
                        'main_office': self.main_office.id,
                        'members_ids': [(6, 0, self.members_ids.ids)],
                        "member_cell_type_id": cell.member_cell_type_id.id,
                    })

                    self.cell_id = new_cell.id

                    new_cell_members = [x.name for x in self.members_ids]
                    

                    for record in cell.members_ids:
                        # check if the name exists in old cell
                        if record.name in new_cell_members:
                            # remove the record from old cell
                            
                            cell.write({
                                        'members_ids': [(3, record.id, False)]
                                        })

                    return {
                        "name": new_cell.name,
                        "view_mode": "form",
                        "res_model": "member.cells",
                        "res_id": new_cell.id,
                        "target": "current",
                        "type": "ir.actions.act_window",
                    }
        