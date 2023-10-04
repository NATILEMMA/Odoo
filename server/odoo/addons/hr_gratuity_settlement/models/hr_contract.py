# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Contract(models.Model):
    _inherit = 'hr.contract'

    training_info = fields.Text(string='Probationary Info', translate=True)
    waiting_for_approval = fields.Boolean()
    is_approve = fields.Boolean(default=False)
    state = fields.Selection(
        selection=[
            ('draft', 'New'),
            ('probation', 'Probation'),
            ('open', 'Running'),
            ('close', 'Expired'),
            ('cancel', 'Cancelled'),
        ],
    )
    # probation_id = fields.Many2one('hr.training')
    # half_leave_ids = fields.Many2many('hr.leave', string="Half Leave")
    training_amount = fields.Float(string='Training Amount', help="amount for the employee during training")

    @api.onchange('date_end')
    def date_correction(self):
        """This function will make sure probation end is less than date_end"""
        for record in self:
            if record.trial_date_end and record.date_end:
                if record.trial_date_end >= record.date_end:
                    raise UserError(_("End Date Can't Be Less Than End of Trial Period"))


    @api.onchange('trial_date_end')
    def state_probation(self):
        """
        function used for changing state draft to probation
        when the end of trail date setting
        """
        for record in self:
            if record.trial_date_end:
                record.state = 'probation'

    # @api.onchange('employee_id')
    # def change_employee_id(self):
    #     """
    #     function for changing employee id of hr.training if changed
    #     """
    #     for record in self:
    #         if record.probation_id and record.employee_id:
    #             record.probation_id.employee_id = record.employee_id.id

    def action_approve(self):
        """
        function used for changing the state probation into
        running when approves a contract
        """
        for record in self:
            record.state = 'open'
            record.is_approve = True

    @api.onchange('state')
    def _change_states(self):
        """This function will check states"""
        for record in self:
            if record.state == 'open':
                record.is_approve = True
    

    # @api.model
    # def create(self, vals_list):
    #     """
    #     function for create a record based on probation
    #     details in a model

    #     """
    #     if vals_list['trial_date_end'] and vals_list['state'] == 'probation':
    #         dtl = self.env['hr.training'].create({
    #             'employee_id': vals_list['employee_id'],
    #             'start_date': vals_list['date_start'],
    #             'end_date': vals_list['trial_date_end'],
    #         })
    #         vals_list['probation_id'] = dtl.id
    #     res = super(Probation, self).create(vals_list)
    #     return res

    def write(self, vals):
        """
        function for checking stage changing and creating probation
        record based on contract stage

        """
        for record in self:
            # if vals.get('state') == 'open' and not record.is_approve:
            #     raise UserError(_("You cannot change the status of non-approved Contracts"))
            if (vals.get('state') == 'cancel' or vals.get('state') == 'close' or vals.get('state') == 'draft') and not record.is_approve:
                raise UserError(_("You cannot change the status of non-approved Contracts"))
            # training_dtl = self.env['hr.training'].search([('employee_id', '=', self.employee_id.id)])
            # if training_dtl:
            #     return super(Probation, self).write(vals)
            # if not training_dtl:
            #     if record.trial_date_end and record.state == 'probation':
            #         self.env['hr.training'].create({
            #             'employee_id': record.employee_id.id,
            #             'start_date': self.date_start,
            #             'end_date': self.trial_date_end,
            #         })
            return super(Contract, self).write(vals)
