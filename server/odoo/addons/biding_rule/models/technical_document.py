from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError


class ProductSelected(models.Model):
    _name = "product.selected"
    _description = "This models will create selected option to product"

    name = fields.Char(translate=True)
    value = fields.Float()
    product_id = fields.Many2one('product.document')


class SelectionField(models.Model):
    _name = 'selection.field_2'
    _description = 'selection field'

    name = fields.Char(string='selection name', required=True, translate=True)
    value = fields.Float(string="selection value", digits=(12, 2))
    vendor_document_id = fields.Many2one('product.document', string='Product document', readonly=True)


class ProductDocument(models.Model):
    _name = 'product.document'
    _description = 'product Documents'

    name = fields.Char(string='Rule name', required=True, copy=False, help='You can give your'
                                                                           'Document number.', translate=True)
    description = fields.Text(string='Description', copy=False, help="Description", translate=True)
    issue_date = fields.Date(string='Issue Date', default=fields.datetime.now(), help="Date of issue", copy=False)
    is_pass = fields.Boolean('passed')
    input_type = fields.Selection(
        [('attach', 'Attach file'),
         ('selection', 'selection'),
         ('tick', 'Yes/No'),
         ], string="Input Type", required=True)

    selection = fields.Many2many('selection.field_2', domain="[('vendor_document_id', '=', 0)]", string='selection')
    agreement = fields.Many2one('purchase.requisition', string='agreement')
    selection_view = fields.Boolean('To see selection')
    number = fields.One2many('number.document_2', 'doc', string='numbering')
    value = fields.Float(string="value in %", digits=(12, 2))

    @api.onchange('selection')
    def get_prices(self):
        for line in self.selection:
            line.vendor_document = self.id

    @api.model
    def create(self, vals):
        if vals['value'] == 0:
            raise UserError(_("The Biding rule amount can not be Zero"))
        all_selected = vals['selection']
        agreement_id = self.env.context.get('active_ids', [])
        vals.update({'agreement': agreement_id[0],
                     'selection_view': True,
                     })
        res = super(ProductDocument, self).create(vals)
        for i in all_selected[0][2]:
            value = self.env['selection.field_2'].search([('id', '=', i)])
            self.env['product.selected'].sudo().create({
                'name': value['name'],
                'value': value['value'],
                'product_id': res.id
            })
        val = 0
        active_id = self.env.context.get('active_id')
        rules = self.env['vendor.document'].search([('agreement', '=', active_id)])
        rule_2 = self.env['product.document'].search([('agreement', '=', active_id)])
        for line in rule_2:
            val = val + line.value
        for line_2 in rules:
            val = val + line_2.value
        if val > 100:
            raise UserError(_("The rule % value have pass 100. The value" + str(val)))

        return res

    def write(self, vals):
        val = 0
        active_id = self.env.context.get('active_id')
        rules = self.env['vendor.document'].search([('agreement', '=', active_id)])
        rule_2 = self.env['product.document'].search([('agreement', '=', active_id)])
        for line in rule_2:
            val = val + line.value
        for line_2 in rules:
            val = val + line_2.value
        try:
            val = val + vals['value'] - self.value
            if val > 100:
                raise UserError(_("The rule % value have pass 100. The value " + str(val)))
        except:
            if val > 100:
                raise UserError(_("The rule % value have pass 100. The value " + str(val)))
        res = super(ProductDocument, self).write(vals)
        return res


class NumberSelection(models.Model):
    _name = 'number.document_2'
    _description = 'numeber Documents'

    amount = fields.Float(string="Amount")
    value = fields.Float(string="value in %", digits=(12, 2))
    doc = fields.Many2one('vendor.document', string='doc')
