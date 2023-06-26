from odoo import api, fields, models


class PayrollHeaderContent(models.Model):

    _name = 'payroll.header'
    _description = 'Bank Report Contents'

    reference_no = fields.Char(string='Payroll Content Reference', required=True,
                          readonly=True, default='New', index=True)
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.company, required=True)
    employee_id = fields.Many2one('hr.employee', string="General Manager", required=True)
    bank_name = fields.Char(string="Bank Name")
    bank_branch = fields.Char(string="Bank Branch")
    company_account = fields.Char(string="Company Account Number")
    content1 = fields.Text(string="First Content")
    content2 = fields.Text(string="Second Content")
    isActive = fields.Boolean(string="Is Active")

    @api.model
    def create(self, vals):
        vals['reference_no'] = self.env['ir.sequence'].next_by_code('payroll.header')
        request = super(PayrollHeaderContent, self).create(vals)
        return request