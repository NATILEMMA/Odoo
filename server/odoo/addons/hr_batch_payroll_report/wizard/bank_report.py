from odoo import models, fields, api, _
import logging
_logger=logging.getLogger(__name__)
 

class BankPayrollBat(models.TransientModel):
    _name = 'batch.payroll'
    _description = "HR  Batch Payroll"


    payroll_month = fields.Date(string="Payroll Month")

    def action_print(self):
        data = dict()
        lines = []   
        payslip_ids = self.env['hr.payslip.run'].search([])
        _logger.info("===============================================")
        _logger.info(len(payslip_ids))
        _logger.info(payslip_ids)
        for rr in payslip_ids:
            xx=0
            for r in rr.slip_ids:
                xx+=r.net
            vals={
                # 'total_net_amount':sum(rr.slip_ids.mapped('net_wage')),
                'total_net_amount':xx,
                'batch_name':rr.name
            }
            lines.append(vals)
            _logger.info("+++++++++++++++++++++++++++++")
            _logger.info(lines)
            data['lines']=lines
        return self.env.ref('hr_batch_payroll_report.report_batch_payroll').report_action(self, data=data)
