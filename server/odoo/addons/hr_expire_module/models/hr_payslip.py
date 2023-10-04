from odoo import api, fields, models


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    payroll_header_id = fields.Many2one('payroll.header', string="Acive Payroll Header", domain=[('isActive', '=', True)])

    @api.model
    def create(self, vals):
        payroll_header = self.env['payroll.header'].search([('isActive', '=', 'true')])
        vals.update({'payroll_header_id': payroll_header[0].id})
        payslip = super(HrPayslipRun, self).create(vals)
        return payslip