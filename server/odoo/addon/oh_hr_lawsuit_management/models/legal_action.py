# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class HrLawsuit(models.Model):
    _name = 'hr.lawsuit'
    _description = 'Hr Lawsuit Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "display_name"

    display_name = fields.Char(store=False, default=lambda self: self.ref_no)

    ref_no = fields.Char(string="Reference Number")

    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id,
                                 help='Name of the company of the user')
    
    party1 = fields.Many2one('res.company', string='Party 1', required=1, readonly=1,
                             help='Choose the company as first Party',
                             states={'draft': [('readonly', False)]})
    party2 = fields.Selection([('employee', 'Employee'),
                               ('partner', 'Partner'),
                               ('other', 'Others')], default='employee',
                              string='Party 2', required=1, readonly=1,
                              help='Choose the second party in the legal issue.It can be Employee, Contacts or others.',
                              states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', string='Employee', copy=False,
                                  readonly=1, states={'draft': [('readonly', False)]},
                                  help='Choose the Employee')
    partner_id = fields.Many2one('res.partner', string='Partner',
                                 copy=False,
                                 readonly=1,
                                 states={'draft': [('readonly', False)]},
                                 help='Choose the partner')
    other_name = fields.Char(string='Name', help='Enter the details of other type')
    party2_name = fields.Char(compute='set_party2', string='Name', store=True)

    case_details = fields.Html(string='Case Details', copy=False, track_visibility='always',
                               help='More details of the case')
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('cancel', 'Cancelled'),
                              ('fail', 'Failed'),
                              ('won', 'Won'),
                              ('reopen','Reopen')], string='Status',
                             default='draft', track_visibility='always', copy=False,
                             help='Status')
    appointment_ids = fields.One2many('lawsuit.appointment_stack', 'law_suit_id')

    appointment_count = fields.Integer(compute='_appointment_count', string='# Appointments', help='Legal appointments', default=0, store="True")

    was_reopen = fields.Boolean(default=False)

    
    def won(self):
        self.state = 'won'
    
    def reopen(self):
        self.was_reopen = True
        self.state = 'reopen'

    def cancel(self):
        self.state = 'cancel'

    def loss(self):
        self.state = 'fail'

    def process(self):
        self.state = 'running'
    
    def lounchWizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment',
            'view_mode': 'form', 
            'target': 'new',
            'res_model': 'wizard.appointment',
            'context': {'parent_obj': self.id} 
        }
    
    def lounchAppointment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'List of appointments',
            'view_mode': 'tree,form', 
            'target': 'self',
            'res_model': 'lawsuit.appointment_stack',
            'create':False,
            'context': {'parent_obj': self.id,},
            'domain':[('law_suit_id', '=', self.id)]
        }
    

    @api.depends('party2', 'employee_id')
    def set_party2(self):
        for each in self:
            if each.party2 == 'employee':
                each.party2_name = each.employee_id.name


    @api.depends('appointment_ids') 
    def _appointment_count(self):
        for each in self:
            each.appointment_count = len(each.appointment_ids)


class HrLegalEmployeeMaster(models.Model):
    _inherit = 'hr.employee'

    legal_count = fields.Integer(compute='_legal_count', string='# Legal Actions', help='Legal actions')

    def _legal_count(self):
        for each in self:
            legal_ids = self.env['hr.lawsuit'].search([('employee_id', '=', each.id)])
            each.legal_count = len(legal_ids)

    def legal_view(self):
        for employee in self:
            legal_ids = self.env['hr.lawsuit'].sudo().search([('employee_id', '=', employee.id)]).ids
            return {
                'domain': str([('id', 'in', legal_ids)]),
                'view_mode': 'tree,form',
                'res_model': 'hr.lawsuit',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'name': _('Legal Actions'),
            }


