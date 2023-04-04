from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError

class VendorSelected(models.Model):
    _name="vendor.selected"
    _description="This models will create selected option to vendor"


    name = fields.Char()
    value = fields.Float()
    vendor_id = fields.Many2one('vendor.document')

class SelectionField(models.Model):
    _name = 'selection.field'
    _description = 'selection field'

    name = fields.Char(string='selection name', required=True)
    value = fields.Float(string="selection value")
    vendor_document_id = fields.Many2one('vendor.document', readonly=True, string='vendor document')


class VendorDocument(models.Model):
    _name = 'vendor.document'
    _description = 'vendor Documents'

    name = fields.Char(string='Rule name', required=True, copy=False, help='You can give your'
                                                                                 'Document number.')
    description = fields.Text(string='Description', copy=False, help="Description")
    issue_date = fields.Date(string='Issue Date', default=fields.datetime.now(), help="Date of issue", copy=False)
    is_pass = fields.Boolean('passed')
    input_type = fields.Selection(
        [('attach', 'Attach file'),
         ('selection', 'selection'),
         ('tick', 'Yes/No'),
         ('employee', 'Man power'),
         ('financial', 'Financial statement'),
         ], string="Input Type")


    selection = fields.Many2many('selection.field', domain="[('vendor_document_id', '=', 0)]", string='selection')
    agreement = fields.Many2one('purchase.requisition', string='agreement')
    selection_view = fields.Boolean('To see selection')
    number = fields.One2many('number.document', 'doc',string='numbering')
    value = fields.Float(string="value in %", required=True, digits=(12, 2))

    @api.model
    def create(self, vals):
        all_selected = vals['selection']
        agreement_id = self.env.context.get('active_ids', [])
        vals.update({'agreement': agreement_id[0],
                      'selection_view': True,
                     })
        res = super(VendorDocument, self).create(vals)
        for i in all_selected[0][2]:
            value = self.env['selection.field'].search([('id', '=', i)])
            self.env['vendor.selected'].sudo().create({
                                                      'name': value['name'],
                                                      'value': value['value'],
                                                      'vendor_id': res.id
                                                      })
        val = 0
        active_id = self.env.context.get('active_id')
        rules = self.env['vendor.document'].search([('agreement', '=', active_id)])
        rule_2 = self.env['product.document'].search([('agreement', '=', active_id)])
        print("rules", rules, "rule_2", rule_2, "active_id", active_id)

        for line in rule_2:
            val = val + line.value
            print("line", val)
        for line_2 in rules:
            val = val + line_2.value
            print("line", val)
            print("vals['value']", vals['value'])
        print("val", val)
        if val > 100:
            raise UserError(_("The rule % value have pass 100"))
        return res

    def write(self, vals):
        val = 0
        active_id = self.env.context.get('active_id')
        vals['agreement'] = active_id
        rules = self.env['vendor.document'].search([('agreement', '=', active_id)])
        rule_2 = self.env['product.document'].search([('agreement', '=', active_id)])
        for line in rule_2:
            val = val + line.value
        for line_2 in rules:
            val = val + line_2.value
        try:
            val = val + vals['value'] - self.value
            if val > 100:
                raise UserError(_("The rule % value have pass 100. The value  "+str(val)))
        except:
            if val > 100:
                raise UserError(_("The rule % value have pass 100. The value "+str(val)))
        res = super(VendorDocument, self).write(vals)
        return


class NumberSelection(models.Model):
    _name = 'number.document'
    _description = 'numeber Documents'

    amount = fields.Float(string="Amount")
    value = fields.Float(string="value in %", digits=(12, 2))
    doc = fields.Many2one('vendor.document', string='doc')
