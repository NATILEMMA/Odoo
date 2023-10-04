
from odoo import api, fields, models, _




class AccountAssetCategory(models.Model):
    _inherit = ['account.asset']
    _description = 'Asset inherit'

    description = fields.Text('Description of Asset', translate=True)
   
    date_of_purchase = fields.Date('Date of purchase')
    location = fields.Char('Location of Asset', translate=True)
    year_of_service = fields.Integer('Year of service')
    depriciation_rate = fields.Integer('Depriciation Rate percentage', compute = "_deperciation_rate_calculate")
    accounts_ref = fields.Char('Account ref', translate=True)


    partner_id = fields.Many2one('res.partner', string='Supplier name',
                                 readonly=True,
                                 states={'draft': [('readonly', False)]}, )
    

    year_of_service = fields.Integer('Year of service')
    depriciation_rate = fields.Integer('Depriciation Rate percentage', compute = "_deperciation_rate_calculate")
    accounts_ref = fields.Char('Account ref', translate=True)
    special_fields_ids = fields.One2many('special.asset.fields','asset_custom_id')
   
    def _deperciation_rate_calculate(self):
        for record in self:
            if record.method == 'linear' and record.purchase_value and record.method_number :
                rate = record.purchase_value / record.method_number 
                record.depriciation_rate = (rate / record.purchase_value) * 100
            elif record.method == 'degressive':
                record.depriciation_rate = record.method_progress_factor  * 100
            else:
                record.depriciation_rate = 0
    
class AccountAssetCategory(models.Model):
    _inherit = ['account.asset.line']
    _description = 'Asset description line inherit'

    cost = fields.Float(related="asset_id.purchase_value" ,string='Cost', readonly=True,)
    description = fields.Text('Description', translate=True)
    remark = fields.Text('Remark', translate=True)


   

class SpecialFieldType(models.Model):
    _name = 'special.asset.fields'
    _description = 'custom dynamic special fields'

    asset_custom_id = fields.Many2one('account.asset')
    field_name = fields.Many2one("special.field.name",string="Field name",required=True)
    field_value = fields.Char(string="Value", translate=True)
  
class SpecialFieldType(models.Model):
    _name = 'special.field.name'
    _description = 'custom dynamic special fields'

    name = fields.Char('Field name', translate=True)




