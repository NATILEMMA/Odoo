from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountAssetDepreciationReport(models.AbstractModel):
    _name = 'report.account_asset_depreciation.depreciation_report_pdf'


    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        date_from =  data['form']['date_from']
        date_to = data['form']['date_to']
        category = data['form']['category']
        lst_end_year = data['form']['lst_end_year']


        self.model = self.env.context.get('active_model')
        
        assets = self.env['account.asset.asset'].search([('depreciation_line_ids.depreciation_date', '>=', date_from),('state', 'not in', ['draft']),('depreciation_line_ids.depreciation_date','<=', date_to),('category_id', 'in', category)])        
        good_assets = []
        total_value = 0  
        total_ly_amount = 0
        total_cy_amount = 0
        total_m_depreciation = 0
        total_sp_amount = 0
        total_remaining = 0
        total_d_value = 0

        for a in assets:        
            lst_year = self.env['account.asset.depreciation.line'].search([('asset_id', '=', a.id), ('move_check', '=', True), ('depreciation_date', '<=', lst_end_year)])
            lst_year_amount = 0
            c_year = self.env['account.asset.depreciation.line'].search([('asset_id', '=', a.id), ('move_check', '=', True), ('depreciation_date', '>', lst_end_year), ('depreciation_date', '<=', date_to)])
            c_year_amount = 0
            s_period = self.env['account.asset.depreciation.line'].search([('asset_id', '=', a.id), ('move_check', '=', True), ('depreciation_date', '>=', date_from), ('depreciation_date', '<=', date_to)])
            s_period_amount= 0
            total_value += a.value                

            for l in lst_year:
                lst_year_amount += l.amount
                a['lst_year_amount'] = lst_year_amount 
            total_ly_amount += lst_year_amount

            for c in c_year:
                c_year_amount += c.amount
                a['c_year_amount'] = c_year_amount
            total_cy_amount += c_year_amount

            for s in s_period:
                s_period_amount += s.amount
                a['s_period_amount'] = s_period_amount
                a['s_remaining_value'] = s.remaining_value
                a['s_depreciated_value'] = s.depreciated_value
            total_d_value += s.depreciated_value
            total_sp_amount += s_period_amount            
            total_remaining += s.remaining_value                
                         
            have_good_lines = self.env['account.asset.depreciation.line'].search([('asset_id', '=', a.id), ('move_check', '=', True)])
            if have_good_lines:
                good_assets.append(a)  

        return {
            'names': good_assets,
            'total_m_depreciation': float(total_m_depreciation),
            'total_cy_amount': float(total_cy_amount),
            'total_ly_amount': float(total_ly_amount),
            'total_sp_amount': float(total_sp_amount),
            'total_d_value': float(total_d_value),
            'total_remaining': float(total_remaining),
            'currency_id': self.env.ref('base.main_company').currency_id,
            'total_value': float(total_value),
            'categories': category,
            'date_from': date_from,
            'date_to': date_to,
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': self.env[self.model].browse(self.env.context.get('active_ids', [])),
            
        }



