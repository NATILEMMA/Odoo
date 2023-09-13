# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)
_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('leader_approved', 'Leader Approved'),
    ('manager_approved', 'Manager Approved'),
    ('rejected', 'Rejected'),
    ('done', 'Done')
]

_STATUS = [
    ('prrequest', 'PR Request'),
    ('rfq', 'RFQ'),
    ('purchase_order', 'Purchase Order')
]


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    request_line_id = fields.Many2one('sprogroup.purchase.request.line',
                                       'Requsition Line Id')

    quotation_flag = fields.Boolean('quotation blag', default=True)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    request_line_id = fields.Many2one('sprogroup.purchase.request.line',
                                      'Requeste Line Id')
    quotation_flag = fields.Boolean('quotation blag', default=True)
    tender = fields.Many2one('purchase.requisition', store=True)

    # def write(self, vals):


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    request_id = fields.Many2one('sprogroup.purchase.request', 'Requeste  Id')
    purchase_type = fields.Selection([('direct', 'Direct purchase'),
                                      ('proforma', 'Proforma Purchase'),
                                      ('limited', 'Limited Tender'),
                                      ('open', 'Open Tender'),
                                      ], 'Purchase Type')

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        if res.requisition_id:
            res.purchase_type = res.requisition_id.purchase_type
            if res.requisition_id.purchase_type == 'limited':
                req = self.env["purchase.order"].search([('requisition_id', '=', res.requisition_id.id)])
                limt = self.env["tender.limit"].search([('limit_by', '=', 'limit')],limit=1)
                if req and limt:
                    if len(req) > limt.max_amount:
                        raise ValidationError(_("You exceed the maximum amount of tender"))

        return res




    # @api.onchange('order_line')
    # def onchange_total_amount(self):
    #     # account_ids = self.env.context.get('active_ids', [])
    #     acc = self.env['sprogroup.purchase.request'].browse(self.request_id.id)
    #     for value in self.order_line:
    #         if value.product_qty != acc.line_ids:
    #             num = 0.0
    #             for line in acc.line_ids:
    #                 if line.product_id.id == value.product_id.id and num == 1:
    #                     if line.product_qty - value.product_qty < 0:
    #                         print("j")
    #                         #raise ValidationError(_("you can not increase quantity"))
    #                     else:
    #                         line._compute_line_state()

    def button_draft(self):
        request = self.env['sprogroup.purchase.request'].search([('id', '=', self.request_id.id)])
        for request_line in request.line_ids:
            print("if", request_line.po_number_2.id, self.id)
            if request_line.po_number_2.id == self.id:
                request_line.invoice_flag = False
                request_line.po_number_2 = False
                request_line.purchased_qty = 0
        return super(PurchaseOrder, self).button_draft()

    def button_confirm(self):
        if self.purchase_type != 'direct' and self.state == 'draft':
             raise ValidationError(_("you can only Direct purchase"))
        request = self.env['sprogroup.purchase.request'].search([('id', '=', self.request_id.id)])
        for request_line in request.line_ids:
            for order_line in self.order_line:
                if order_line.product_id == request_line.product_id and request_line.invoice_flag == False and request_line.purchased_qty != 0:
                    if (request_line.product_qty - request_line.purchased_qty) - order_line.product_qty < 0:
                        raise ValidationError(_("you can not increase quantity"))
                    vals = {
                        "request_id": request_line.request_id.id,
                        "product_qty": request_line.product_qty - request_line.purchased_qty,
                        "purchased_qty": order_line.product_qty,
                        "request_id": request_line.request_id.id,
                        "product_id": request_line.product_id.id,
                        "product_uom_id": request_line.product_uom_id.id,
                        "name": request_line.name,
                        "analytic_acount": self.order_line.account_analytic_id.id,
                        "po_number_2": self.id,

                    }
                    # if not request_line:
                    #     request_line.po_number_2 = self.id
                    request_line.invoice_flag = True
                    # print("request_line", request_line.po_number, self.id)
                    self.env['sprogroup.purchase.request.line'].create(vals)
                elif order_line.product_id == request_line.product_id and request_line.invoice_flag == False and request_line.purchased_qty == 0:
                    if (request_line.product_qty - request_line.purchased_qty) - order_line.product_qty < 0:
                        raise ValidationError(_("you can not increase quantity"))

                    request_line.write({
                        "purchased_qty": order_line.product_qty,
                        # "po_number_2": self.id,
                        "remaining_checked": False,
                    })
                    print("new", request_line.po_number_2)
                    if not request_line.po_number_2:
                        request_line.po_number_2 = self.id
        return super(PurchaseOrder, self).button_confirm()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    payment_flag = fields.Boolean('Purchase Payment')


class HrExpense(models.Model):
    _inherit = "hr.expense"
    purchase_request_id = fields.Many2one('sprogroup.purchase.request')

    @api.onchange('total_amount')
    def onchange_total_amount(self):

        for record in self:
            # _logger.info("--------unit_amount=s%s",self.unit_amount)	

            if record.purchase_request_id:

                error_message = ''
                purchase_request_lines = self.env['sprogroup.purchase.request.line'].search(
                    [('id', '=', self.purchase_request_id.id)]).ids

                purchase_request_lines_ary = self.env['sprogroup.purchase.request.line'].browse(purchase_request_lines)
                _logger.info("--------purchase_request_lines_ary=s%s", purchase_request_lines_ary)

                for purchase_request_line in purchase_request_lines_ary:

                    total_price = purchase_request_line.product_qty * purchase_request_line.estimated_price
                    _logger.info("--------purchase_request_line.product_qty=s%s", purchase_request_line.product_qty)
                    _logger.info("--------total_price=s%s", total_price)

                    if self.total_amount > total_price:
                        error_message = 'the price exceeds maximum amount'
                        raise UserError(error_message)


class SprogroupPurchaseRequest(models.Model):
    _name = 'sprogroup.purchase.request'
    _description = 'Sprogroup Purchase Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_("You can delete only draft state purchase"))
        return super(SprogroupPurchaseRequest, self).unlink()

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('sprogroup.purchase.request')

    @api.model
    def _get_default_label(self):
        for current_label in self:
            current_label.label = self.purchase_request_id.name

    @api.onchange('description')
    def onchange_description(self):

        if self.state == 'done':
            self.description = self.name
            self.name = self.code

    @api.model
    @api.depends('line_ids.total_price')
    def _amount_all(self):
        for order in self:
            amount_total = 0
            for line in order.line_ids:
                amount_total += line.estimated_price * line.product_qty

            order.update({
                'amount_total': amount_total,
            })

    max_qty = fields.Float(string='max qty', store=True)
    amount_total = fields.Float(string='Total', store=True, compute='_amount_all')
    description = fields.Char('Request Name', size=32, required=True,translate=True)
    name = fields.Char('Name', size=32, required=True,translate=True )
    code = fields.Char('Code', size=32, required=True, default=_get_default_name, track_visibility='onchange',translate=True)
    current_label = fields.Char('Label', size=32, default=_get_default_label, track_visibility='onchange',translate=True)
    date_start = fields.Date('Start date',
                             help="Date when the user initiated the request.",
                             default=fields.Date.context_today,
                             track_visibility='onchange')
    end_start = fields.Date('End date', default=fields.Date.context_today,
                            track_visibility='onchange')
    requested_by = fields.Many2one('res.users',
                                   'Requested by',
                                   required=True,
                                   track_visibility='onchange',
                                   default=_get_default_requested_by)
    assigned_to = fields.Many2one('res.users', 'Approver', required=True,
                                  track_visibility='onchange')
    description = fields.Text('Description',translate=True)

    line_ids = fields.One2many('sprogroup.purchase.request.line', 'request_id',
                               'Products to Purchase',
                               readonly=False,
                               copy=True, )
    state = fields.Selection(selection=_STATES,
                             string='Status',
                             index=True,
                             track_visibility='onchange',
                             required=True,
                             copy=False,
                             default='draft')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    purchase_type = fields.Selection([('direct', 'Direct purchase'),
                                      ('proforma', 'Proforma Purchase'),
                                      ('limited', 'Limited Tender'),
                                      ('open', 'Open Tender'),
                                     ],'Purchase Type',)
    is_direct = fields.Boolean("is direct", default=False)
    is_proforma = fields.Boolean("is proforma", default=False)
    is_limited = fields.Boolean("is limited", default=False)
    is_open = fields.Boolean("is open", default=False)
    purchase_count = fields.Integer(
        compute="_purchase_count", string="purchase quotation Count")

    def _purchase_count(self):
        obj = self.env['purchase.order'].search([('request_id', '=', self.id)])
        for serv in self:
            serv.purchase_count = obj.search_count([('request_id', '=', self.id)])



    @api.onchange('state')
    def onchange_state(self):
        assigned_to = None
        if self.state:
            if (self.requested_by.id == False):
                self.assigned_to = None
                return

            employee = self.env['hr.employee'].search([('work_email', '=', self.requested_by.email)])
            if (len(employee) > 0):
                if (employee[0].department_id and employee[0].department_id.manager_id):
                    assigned_to = employee[0].department_id.manager_id.user_id

        self.assigned_to = assigned_to

    @api.depends('requested_by')
    def _compute_department(self):
        if (self.requested_by.id == False):
            self.department_id = None
            return

        employee = self.env['hr.employee'].search([('work_email', '=', self.requested_by.email)])
        if (len(employee) > 0):
            self.department_id = employee[0].department_id.id
        else:
            self.department_id = None

    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department', store=True, )

    @api.depends('state')
    def _compute_can_leader_approved(self):
        current_user_id = self.env.uid
        if (self.state == 'to_approve' and current_user_id == self.assigned_to.id):
            self.can_leader_approved = True
        else:
            self.can_leader_approved = False
        print("_compute_can_manager_approved", self.can_manager_approved)

    can_leader_approved = fields.Boolean(string='Can Leader approved', compute='_compute_can_leader_approved')

    @api.depends('state')
    def _compute_can_manager_approved(self):
        print("_compute_can_manager_approved")
        current_user = self.env['res.users'].browse(self.env.uid)

        if (self.state == 'leader_approved' and current_user.has_group(
                'purchase_request.group_sprogroup_purchase_request_manager')):
            self.can_manager_approved = True
        else:
            self.can_manager_approved = False
        print("_compute_can_manager_approved",self.can_manager_approved, current_user)

    can_manager_approved = fields.Boolean(string='Can Manager approved', compute='_compute_can_manager_approved')

    @api.depends('state')
    def _compute_can_reject(self):
        self.can_reject = (self.can_leader_approved or self.can_manager_approved)

    can_reject = fields.Boolean(string='Can reject', compute='_compute_can_reject')

    @api.depends('state')
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ('to_approve', 'leader_approved', 'manager_approved', 'rejected', 'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    is_editable = fields.Boolean(string="Is editable",
                                 compute="_compute_is_editable",
                                 readonly=True)

    @api.model
    def create(self, vals):

        request = super(SprogroupPurchaseRequest, self).create(vals)
        if vals.get('assigned_to'):
            request.message_subscribe(partner_ids=[request.assigned_to.partner_id.id])
        return request

    def write(self, vals):

        _logger.info("--------vals=%s", vals)
        res = super(SprogroupPurchaseRequest, self).write(vals)
        for request in self:
            if vals.get('assigned_to'):
                self.message_subscribe(partner_ids=[request.assigned_to.partner_id.id])
        return res

    def button_draft(self):
        self.is_limited = False
        self.is_proforma = False
        self.is_direct = False
        self.is_open = False
        self.mapped('line_ids').do_uncancel()
        return self.write({'state': 'draft'})

    def button_to_approve(self):
        flag = False
        for line in self.line_ids:
            try:
                line.date_required = self.date
            except:
                line.date_required = datetime.today()
            flag = True
        if not flag:
            raise ValidationError(_("The purchase request is empty"))
        return self.write({'state': 'to_approve'})

    def button_leader_approved(self):
        return self.write({'state': 'leader_approved'})

    def button_manager_approved(self):
        print(self.purchase_type)
        if self.purchase_type == False:
            raise ValidationError(_("You have not select Purchase Type"))
        if self.purchase_type == 'direct':
            self.is_direct = True
        if self.purchase_type == 'proforma':
            self.is_proforma = True
        if self.purchase_type == 'open':
            self.is_open = True
        if self.purchase_type == 'limited':
            self.is_limited = True
        for rec in self:
            can_approve = False
            error_message = ''
        purchase_request_lines = self.env['sprogroup.purchase.request.line'].search([('request_id', '=', self.id)]).ids
        purchase_request_lines_ary = self.env['sprogroup.purchase.request.line'].browse(purchase_request_lines)
        for purchase_request_line in purchase_request_lines_ary:
            product_id = purchase_request_line.product_id
            total_price = purchase_request_line.product_qty * purchase_request_line.estimated_price
            approval_limits = self.env['purchase.approval.limit'].search([('user_id', '=', self.env.user.id)]).ids
            if approval_limits:
                amount_limits_ary = self.env['purchase.approval.limit'].browse(approval_limits)
                for amount_limit in amount_limits_ary:
                        if amount_limit.user_id.id == self.env.user.id:
                            max_amount = amount_limit.max_amount
                            if total_price <= max_amount:
                                can_approve = True
                            else:
                                    raise ValidationError(_("You Exceeded Your Maximum Limit"))
                        else:

                            can_approve = False
                            error_message = 'User doesnt Have Approval Limit'
            else:
                    raise ValidationError(_("User doesnt Have Approval Limit"))

            if can_approve:
                return self.write({'state': 'manager_approved'})
            else:
                raise ValidationError(_("User doesnt Have Approval Limit"))

    def button_rejected(self):
        self.mapped('line_ids').do_cancel()
        return self.write({'state': 'rejected'})

    def button_done(self):

        return self.write({'state': 'done'})

    def button_request_payment(self):
        template_id = self.env['product.template'].search([('payment_flag', '=', True)], limit=1).id
        product_ids = self.env['product.product'].search([('product_tmpl_id', '=', template_id)]).id

        self.write({'state': 'done'})
        return {
            'name': 'Payment',
            'res_model': 'hr.expense',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'nodestroy': True,
            'target': 'current',
            'context': {
                'default_request_id': self.id,
                'default_unit_amount': self.amount_total,
                'default_product_id': product_ids
            }
        }

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({'state': 'rejected'})

    def make_purchase_agreement_limted(self):
        valid = False
        for pro in self.line_ids:
            if pro.product_qty - pro.purchased_qty > 0:
                valid = True
        if not valid:
            raise ValidationError(_("you have purchase all the requested quantity"))

        view_id = self.env.ref('purchase_requisition.view_purchase_requisition_form')
        order_line = []
        for line in self.line_ids:
            product = line.product_id
            fpos = self.env['account.fiscal.position']
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
                taxes_id = fpos.map_tax(
                    product.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
            else:
                taxes_id = fpos.map_tax(product.supplier_taxes_id)
            if line.request_line_state == "pr_request" or line.request_line_state == "p_rfq":
                if not line.invoice_flag and line.product_qty - line.purchased_qty != 0:
                    product_line = (0, 0, {
                        'product_id': product.id,
                        'request_line_id': line.id,
                        # 'state': 'draft',
                        'product_uom_id': product.uom_po_id.id,
                        'price_unit': 0,
                        # 'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        # 'taxes_id' : ((6,0,[taxes_id.id])),
                        'product_qty': line.product_qty - line.purchased_qty,
                    })

                    order_line.append(product_line)
        if order_line:
            return {
                'name': _('New'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.requisition',
                'view_mode': 'form',
                'target': 'current',
                'view_id': view_id.id,
                'views': [(view_id.id, 'form')],
                'context': {
                    # 'default_purchase_requisition_id': self.id,
                    'default_line_ids': order_line,
                    'default_state': 'draft',
                    'default_origin': self.name,
                    'default_purchase_type': self.purchase_type,
                    # 'default_request_id': self.id,
                    'default_user_id': self.requested_by.id,
                    'default_request_line_id': self.id

                }
        }

    def make_purchase_agreement(self):
        valid = False
        for pro in self.line_ids:
            if pro.product_qty - pro.purchased_qty > 0:
                valid = True
        if not valid:
            raise ValidationError(_("you have purchase all the requested quantity"))

        view_id = self.env.ref('purchase_requisition.view_purchase_requisition_form')
        order_line = []
        for line in self.line_ids:
            product = line.product_id
            fpos = self.env['account.fiscal.position']
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
                taxes_id = fpos.map_tax(
                    product.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
            else:
                taxes_id = fpos.map_tax(product.supplier_taxes_id)
            if line.request_line_state == "pr_request" or line.request_line_state == "p_rfq":
                if not line.invoice_flag and line.product_qty - line.purchased_qty != 0:
                    product_line = (0, 0, {
                        'product_id': product.id,
                        'request_line_id': line.id,
                        # 'state': 'draft',
                        'product_uom_id': product.uom_po_id.id,
                        'price_unit': 0,
                        # 'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        # 'taxes_id' : ((6,0,[taxes_id.id])),
                        'product_qty': line.product_qty - line.purchased_qty,
                    })

                    order_line.append(product_line)
        if order_line:
            return {
                'name': _('New'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.requisition',
                'view_mode': 'form',
                'target': 'current',
                'view_id': view_id.id,
                'views': [(view_id.id, 'form')],
                'context': {
                    # 'default_purchase_requisition_id': self.id,
                    'default_line_ids': order_line,
                    'default_state': 'draft',
                    'default_origin': self.name,
                    'default_purchase_type': self.purchase_type,
                    # 'default_request_id': self.id,
                    'default_user_id': self.requested_by.id,
                    'default_request_line_id': self.id

                }
        }

    def make_purchase_quotation(self):
        valid = False
        for pro in self.line_ids:
            if pro.product_qty - pro.purchased_qty > 0:
                valid = True
        if not valid:
            raise ValidationError(_("you have purchase all the requested quantity"))
        view_id = self.env.ref('purchase.purchase_order_form')
        order_line = []
        for line in self.line_ids:
            product = line.product_id
            print("product", product, line.request_line_state)
            fpos = self.env['account.fiscal.position']
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
                taxes_id = fpos.map_tax(
                    line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
            else:
                taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id)

            if line.request_line_state == "pr_request" or line.request_line_state == "p_rfq":
                if not line.invoice_flag and line.product_qty - line.purchased_qty != 0:
                    product_line = (0, 0, {
                        'product_id': line.product_id.id,
                        'request_line_id': line.id,
                        'state': 'draft',
                        'product_uom': line.product_id.uom_po_id.id,
                        'price_unit': 0,
                        'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        # 'taxes_id' : ((6,0,[taxes_id.id])),
                        'product_qty': line.product_qty - line.purchased_qty,
                        'name': line.product_id.name,
                        'account_analytic_id': line.analytic_acount.id
                    })
                    order_line.append(product_line)
                    print("self.id..dersual", self.id)
        if order_line:
            return {
                'name': _('New Quotation'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'target': 'current',
                'request_id': self.id,
                'view_id': view_id.id,
                'views': [(view_id.id, 'form')],
                'context': {
                    'default_request_id': self.id,
                    'default_order_line': order_line,
                    'default_purchase_type': self.purchase_type,
                    'default_state': 'draft',
                    'default_request_id': self.id,
                }
            }

    def make_purchase_proforma(self):
        valid = False
        for pro in self.line_ids:
            if pro.product_qty - pro.purchased_qty > 0:
                valid = True
        if not valid:
            raise ValidationError(_("you have purchase all the requested quantity"))
        view_id = self.env.ref('purchase.purchase_order_form')
        order_line = []
        for line in self.line_ids:
            product = line.product_id
            print("product", product, line.request_line_state)
            fpos = self.env['account.fiscal.position']
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
                taxes_id = fpos.map_tax(
                    line.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
            else:
                taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id)

            if line.request_line_state == "pr_request" or line.request_line_state == "p_rfq":
                if not line.invoice_flag and line.product_qty - line.purchased_qty != 0:
                    product_line = (0, 0, {
                        'product_id': line.product_id.id,
                        'request_line_id': line.id,
                        'state': 'draft',
                        'product_uom': line.product_id.uom_po_id.id,
                        'price_unit': 0,
                        'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        # 'taxes_id' : ((6,0,[taxes_id.id])),
                        'product_qty': line.product_qty - line.purchased_qty,
                        'name': line.product_id.name,
                        'account_analytic_id': line.analytic_acount.id
                    })
                    order_line.append(product_line)
                    print("self.id..dersual", self.id)
        if order_line:
            return {
                'name': _('New Quotation'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'form',
                'target': 'current',
                'request_id': self.id,
                'view_id': view_id.id,
                'views': [(view_id.id, 'form')],
                'context': {
                    'default_request_id': self.id,
                    'default_purchase_type': self.purchase_type,
                    'default_order_line': order_line,
                    'default_state': 'draft',
                    'default_request_id': self.id,
                }
            }


class SprogroupPurchaseRequestLine(models.Model):
    _name = "sprogroup.purchase.request.line"
    _description = "Sprogroup Purchase Request Line"
    _inherit = ['mail.thread']

    # max_qty = fields.Float(string='Maximum QTY')

    def _compute_line(self):

        for rec in self:
            purchase_line = self.env['purchase.requisition.line'].search([('request_line_id', '=', rec.id)]).ids

            if purchase_line:
                purchased_qty = 0
                _logger.info("--fffffffffffffuuuuuuuuuuuuuu------purchase_line=%s", purchase_line)
                purchase_lines = self.env['purchase.order.line'].browse(purchase_line)
                _logger.info("--------purchase_lines=%s", purchase_lines)
                for line in purchase_lines:
                    _logger.info("--------product_qty=%s", line.product_qty)
                    rec.po_number = line.order_id
                    purchased_qty = purchased_qty + line.product_qty

                    _logger.info("-----rec.purchased_qty---%s", rec.purchased_qty)
                    _logger.info("-----rec.product_qty---%s", rec.product_qty)
                    if rec.purchased_qty > 0 and rec.product_qty != rec.purchased_qty and rec.remaining_checked == False:
                        vals = {
                            "request_id": rec.request_id.id,
                            "product_qty": rec.product_qty - rec.purchased_qty,
                            "purchased_qty": 0,
                            "request_id": rec.request_id.id,
                            "product_id": rec.product_id.id,
                            "product_uom_id": rec.product_uom_id.id,
                            "name": rec.name,

                        }
                        _logger.info("--------%s", vals)
                        rec.remaining_checked = True
                        self.env['sprogroup.purchase.request.line'].create(vals)

                    # if rec.product_qty < 0:
                    #     raise ValidationError(_("you can not order above the request"))

                    if line.state == 'purchase':
                        rec.request_line_state = 'purchase_order'
                    else:
                        rec.request_line_state = 'rfq'

                    rec.purchased_qty = purchased_qty
            else:
                _logger.info("--------else")
                rec.purchased_qty = 0
                rec.request_line_state = 'pr_request'
                # rec.po_number_2 = 0

    def _compute_line_state(self):
        print("self")
        for rec in self:
            #     purchase_line = self.env['purchase.order.line'].search([('request_line_id', '=', rec.id)]).ids
            #     if purchase_line:
            #         purchased_qty=0
            #         _logger.info("--f------purchase_line=%s",purchase_line)
            #         purchase_lines = self.env['purchase.order.line'].browse(purchase_line)
            #         _logger.info("--------purchase_lines=%s",purchase_lines)
            #         for line in purchase_lines:
            #             _logger.info("--------product_qty=%s",line.product_qty)
            #             rec.po_number=line.order_id
            #             purchased_qty=purchased_qty + line.product_qty

            #             _logger.info("-----rec.purchased_qty---%s",rec.purchased_qty)
            #             _logger.info("-----rec.product_qty---%s",rec.product_qty)
            #             if rec.purchased_qty >0 and rec.product_qty != rec.purchased_qty and rec.remaining_checked == False:
            #                 vals={
            #                 "request_id":rec.request_id.id,
            #                 "product_qty":rec.product_qty - rec.purchased_qty,
            #                 "purchased_qty":0,
            #                 "request_id":rec.request_id.id,
            #                 "product_id":rec.product_id.id,
            #                 "product_uom_id":rec.product_uom_id.id,
            #                 "name":rec.name,

            #                 }
            #                 _logger.info("--------%s",vals)
            #                 rec.remaining_checked=True
            #                 self.env['sprogroup.purchase.request.line'].create(vals)

            #             if rec.product_qty < 0:
            #                 raise ValidationError(_("you can not order above the request"))

            #             if line.state == 'purchase':
            #                 rec.request_line_state='purchase_order'
            #             else:
            #                 rec.request_line_state='rfq'

            #             rec.purchased_qty=purchased_qty
            #     else:
            # _logger.info("--------else")
            # rec.purchased_qty=0
            rec.request_line_state = 'pr_request'
            # rec.po_number = 0

    def _compute_supplier_id(self):
        for rec in self:
            if rec.product_id:
                if rec.product_id.seller_ids:
                    rec.supplier_id = rec.product_id.seller_ids[0].name

    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('purchase_ok', '=', True)], required=True,
        track_visibility='onchange')
    name = fields.Char('Description', size=256,
                       track_visibility='onchange',translate=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product UOM',
                                     track_visibility='onchange', readonly=True)
    product_qty = fields.Float(string='Requested QTY', digits=dp.get_precision('Product Unit of Measure'))
    purchased_qty = fields.Float(string='Purchased QTY', compute="_compute_line_state", store=True)
    request_id = fields.Many2one('sprogroup.purchase.request',
                                 'Purchase Request',
                                 ondelete='cascade', readonly=True, store=True)
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 store=True, readonly=True)
    requested_by = fields.Many2one('res.users',
                                   related='request_id.requested_by',
                                   string='Requested by',
                                   store=True, readonly=True)
    assigned_to = fields.Many2one('res.users',
                                  related='request_id.assigned_to',
                                  string='Assigned to',
                                  store=True, readonly=True)
    date_start = fields.Date(related='request_id.date_start',
                             string='Request Date', readonly=True,
                             store=True)
    end_start = fields.Date(related='request_id.end_start',
                            string='End Date', readonly=True,
                            store=True)
    description = fields.Text(related='request_id.description',
                              string='Description', readonly=True,
                              store=True,translate=True)
    date_required = fields.Date(string='Request Date',
                                track_visibility='onchange',
                                default=fields.Date.context_today)

    specifications = fields.Text(string='Specifications',translate=True)
    request_state = fields.Selection(string='Request state',
                                     readonly=True,
                                     related='request_id.state',
                                     selection=_STATES,
                                     store=True)
    request_status = fields.Selection(string='Status',
                                      selection=_STATUS
                                      )
    po_number = fields.Many2one('purchase.order', string='Po Number', compute="_compute_line_state")
    po_number_2 = fields.Many2one('purchase.order', readonly=True, string='Po Number')
    analytic_acount = fields.Many2one('account.analytic.account', string='Analytic Account', required=True,)

    estimated_price = fields.Float(string='Estimeted Price', default='1')
    total_price = fields.Float('Total Price', compute="_compute_total", track_visibility='onchange')
    request_line_state = fields.Selection(string='Status',
                                          selection=[
                                              ('pr_request', 'PR Request'),
                                              ('p_rfq', 'Partial RFQ'),
                                              ('rfq', 'RFQ'),
                                              ('purchase_order', 'Purchase Order')
                                          ], compute="_compute_line_state"
                                          )
    supplier_id = fields.Many2one('res.partner',
                                  string='Preferred supplier',
                                  compute="_compute_supplier_id")

    cancelled = fields.Boolean(
        string="Cancelled", readonly=True, default=False, copy=False)
    remaining_checked = fields.Boolean(
        string="Checked", readonly=True, default=False)
    invoice_flag = fields.Boolean('quotation blag', default=False)

    # @api.onchange('product_qty')
    # def onchange_qty(self):
    #     _logger.info("----------------------onchange=s%s")	
    #     _logger.info("-------------------- self.product_qty =s%s", self.product_qty )	

    #     if self.product_qty < 0:

    #         raise ValidationError(_("you can not order above the request"))  

    @api.depends('request_status')
    def _compute_is_visible(self):
        for rec in self:
            if rec.state in ('done'):
                rec.is_visible = False
            else:
                rec.is_visible = True

    is_visible = fields.Boolean(string="Is editable",
                                compute="_compute_is_visible",
                                visible=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = self.product_id.name

    @api.depends('estimated_price', 'product_qty')
    def _compute_total(self):
        for record in self:
            record.total_price = record.product_qty * record.estimated_price

    def do_cancel(self):
        """Actions to perform when cancelling a purchase request line."""
        self.write({'cancelled': True})

    def do_uncancel(self):
        """Actions to perform when uncancelling a purchase request line."""
        self.write({'cancelled': False})

    def _compute_is_editable(self):
        for rec in self:
            if rec.request_id.state in ('to_approve', 'leader_approved', 'manager_approved', 'rejected',
                                        'done'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    is_editable = fields.Boolean(string='Is editable',
                                 compute="_compute_is_editable",
                                 readonly=True)

    def write(self, vals):
        res = super(SprogroupPurchaseRequestLine, self).write(vals)
        if vals.get('cancelled'):
            requests = self.mapped('request_id')
            requests.check_auto_reject()
        return res


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    request_line_id = fields.Many2one('sprogroup.purchase.request',
                                      'Requsition Line Id')
    purchase_type = fields.Selection([('direct', 'Direct purchase'),
                                      ('proforma', 'Proforma Purchase'),
                                      ('limited', 'Limited Tender'),
                                      ('open', 'Open Tender'),
                                      ], 'Purchase Type')

    def action_in_progress(self):
        if self.purchase_type == 'limited':
           search = self.env["tender.limit"].search([('limit_by', '=', 'limit')])
           if len(search) == 0:
               raise ValidationError(_("Please configer rule for Limited tender"))
        elif self.purchase_type == 'open' :
            search = self.env["tender.limit"].search([('limit_by', '=', 'open Tender')])
            if len(search) == 0:
                raise ValidationError(_("Please configer rule for Limited tender"))
        return super(PurchaseRequisition, self).action_in_progress()


