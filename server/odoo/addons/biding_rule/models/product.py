from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel_3 = fields.Many2one('biding.product', string="Attachment", invisible=1)
    attach_rel_2 = fields.Many2many('vendor.partner', string="Attachment", invisible=1)


class BidingProduct(models.Model):
    _name = 'biding.product'
    _description = 'biding product'
    #
    name = fields.Char(string='Rule name')
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel_3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    is_pass = fields.Boolean('passed')
    input_type = fields.Selection(
        [('attach', 'Attach file'),
         ('selection', 'selection'),
         ('tick', 'Yes/No'),
         ], string="Input Type")
    amount = fields.Float(string="Amount")
    rule = fields.Many2one('product.document', string='rule')
    selection = fields.Many2one('product.selected', domain="[('product_id', '=', rule)]", string='selection')
    purchase = fields.Many2one('purchase.order', string='vendor')
    value = fields.Float(string="value in %", required=True, digits=(12, 2))




class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = 'Purchase Order'

    rule = fields.One2many('biding.product', 'purchase', string='rule')
    agreement = fields.Many2one('purchase.requisition', related='requisition_id', string='Purchase agreement')
    state_of_requisition = fields.Selection(related='requisition_id.state')
    status = fields.Selection([('failed', 'Failed'), ('passed', 'Passed')])
    from_tendor = fields.Boolean(default=False)

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        for record in self:
            res = super(PurchaseOrder, self)._onchange_requisition_id()
            if record.requisition_id:
                record.from_tendor = True
            else:
                record.from_tendor = False
            return res

    def button_approve_new(self):
        if self.requisition_id:
            if self.requisition_id.state == 'open':
                self.state = 'to approve'
                print("button_to_approve")
                activity_type = self.env['mail.activity.type'].search([('name', '=', 'Purchase Approval')], limit=1)
                model = self.env['ir.model'].search([('model', '=', 'purchase.order'), ('is_mail_activity', '=', True)])
                message = self.name
                print("activity_type", activity_type, "model", model)
                self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Approval",
                    'date_deadline': date.today(),
                    'user_id': self.requisition_id.approver_id.id,
                    'res_model_id': model.id,
                    'res_id': self.id,
                    'activity_type_id': activity_type.id
                })
                self.requisition_id.approver_id.notify_warning(message, '<h4>Purchase Tender Approval Approval</h4>',
                                                               True)
            else:
                raise UserError(_("The Biding is not in selection process"))

    def button_approved(self):
        orders = self.env['purchase.order'].search([('requisition_id', '=', self.requisition_id.id)])
        if self.requisition_id:
            self.requisition_id.state = 'financial'
        for order in orders:
            if order != self:
                order.write({'state': 'cancel'})
        return super(PurchaseOrder, self).button_approve()

    def button_confirm(self):
        """This function will make change the status of the not selected vendors to Cancel"""
        orders = self.env['purchase.order'].search([('requisition_id', '=', self.requisition_id.id)])
        print(orders)
        print(self)
        for order in orders:
            if order != self:
                order.write({'state': 'cancel'})
        if self.requisition_id and self.state == 'draft':
            raise UserError(_("You cannot confirm purchase which is in biding process"))
        return super(PurchaseOrder, self).button_confirm()

    @api.onchange('partner_id')
    def _make_agreement_change(self):
        """This function will determine the value of agreement in partner"""
        for record in self:
            if self.requisition_id:
                active_id = self.env.context.get('active_id')
                record.partner_id.agreement = active_id
                record.partner_id.rule = [(6, 0, [])]
                if not record.partner_id.rule:
                    rules = self.env['vendor.document'].search([('agreement', '=', record.partner_id.agreement.id)])
                    terms = []
                    for rule in rules:
                        values = {}
                        values['name'] = rule.name
                        values['input_type'] = rule.input_type
                        values['rule'] = rule.id
                        values['value'] = rule.value

                        terms.append((0, 0, values))
                    record.partner_id.rule = terms
                record.partner_id.is_tender = True

    @api.onchange('agreement')
    def onchange_input_type(self):
        if self.rule:
            self.rule = [(6, 0, 0)]
        rules = self.env['product.document'].search([('agreement', '=', self.agreement.id)])
        terms = []
        for rule in rules:
            values = {}
            values['name'] = rule.name
            values['input_type'] = rule.input_type
            values['rule'] = rule.id
            values['value'] = rule.value

            terms.append((0, 0, values))
        self.rule = terms


class PurchaseOrderLineInherit(models.Model):
    _inherit = "purchase.order.line"

    status = fields.Selection([('failed', 'Failed'), ('passed', 'Passed')])
