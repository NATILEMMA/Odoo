from collections import defaultdict
from distutils.log import error
from itertools import groupby
from re import search

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import float_is_zero, OrderedSet
from datetime import timedelta
from datetime import datetime, time
# from multiprocessing import Process
import logging

_logger = logging.getLogger(__name__)


class Payment_request(models.Model):
    _name = "transfer.request"
    _description = "Stock Transfer"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    pr = fields.Many2one('sprogroup.purchase.request', "PR")
    name = fields.Char(
        'Reference', default='/',
        copy=False, index=True, readonly=True)
    note = fields.Text('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting For Approval'),
        ('approved', 'Approve'),
        ('done', 'Recieved'),
        ('return', 'Returned'),
        ('cancel', 'Cancel')

    ], string='Status',
        copy=False, index=True, readonly=True, store=True, tracking=True, default="draft")
    date = fields.Datetime(
        'Creation Date',
        default=fields.Datetime.now, index=True, tracking=True,
        help="Creation Date, usually the time of the order",
        states={'approved': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    scheduled_date = fields.Datetime('Scheduled date', default=fields.Datetime.now, copy=False,
                                     help="Date at which the transfer has been processed or cancelled.",
                                     states={'approved': [('readonly', True)], 'done': [('readonly', True)],
                                             'cancel': [('readonly', True)]})
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_src_id,
        states={'approved': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_dest_id,
        states={'approved': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        states={'approved': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    user_id = fields.Many2one(
        'res.users', 'Request_by', default=lambda self: self.env.user, readonly=True, )
    approved_id = fields.Many2one(
        'res.users', 'Approved_by', readonly=True, )
    received_id = fields.Many2one(
        'hr.employee', 'Received by')
    canceled_id = fields.Many2one(
        'res.users', 'Canceled_by', readonly=True)

    item_ids = fields.One2many('transfer.request.item', 'transfer_request_id', 'Items',
                               states={'approved': [('readonly', True)], 'cancel': [('readonly', True)],
                                       'done': [('readonly', True)]})
    stock_picking = fields.Many2one('stock.picking', 'Transfer', readonly=True)
    Approver = fields.Many2one('res.users', string='Approver',
                               domain=lambda self: [("groups_id", "=", self.env.ref("stock.group_stock_manager").id)],
                               required=True)

    message = fields.Char("Message")
    asset = fields.Boolean("Is Asset")
    invoice_count_3 = fields.Integer(
        compute="_compute_count_invoice_3", string="expanse Count")

    invoice_count_4 = fields.Integer(
        compute="_compute_count_invoice_4", string="expanse Count")

    def _compute_count_invoice_3(self):
        obj = self.env['stock.picking']
        for serv in self:
            serv.invoice_count_3 = obj.search_count([('stock_request', '=', self.id)])
        print("serv.invoice_count", serv.invoice_count_3)

    def _compute_count_invoice_4(self):
        obj = self.env['sprogroup.purchase.request']
        for serv in self:
            serv.invoice_count_4 = obj.search_count([('sr', '=', self.id)])
        print("serv.invoice_count", serv.invoice_count_3)

    @api.model
    def create(self, vals):
        res = super(Payment_request, self).create(vals)
        name = self.env['ir.sequence'].next_by_code('transfer.request')
        res.write({'name': name})
        return res

    def action_request(self):
        print("self.received_id",self.received_id)
        if not self.received_id:
            usr = self.env.user.id
            model = self.env['hr.employee'].search([('user_id', '=', usr)])
            self.received_id = model.id
        if not self.item_ids:
            raise UserError("Please select product for your request")
        user_id = self.Approver
        model = self.env['ir.model'].search([('model', '=', 'transfer.request')])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'To Do')], limit=1)
        print("activity_type", activity_type)
        message = str(self.name) + "'stock request must be approve."
        activity = self.env['mail.activity'].sudo().create({
            'display_name': message,
            'summary': "renewal",
            'date_deadline': self.scheduled_date,
            'user_id': user_id.id,
            'res_model_id': model.id,
            'res_id': self.id,
            'activity_type_id': activity_type.id
        })
        user_id.notify_warning(message, '<h4>Stock request Approval</h4>', True)
        self.state = 'waiting'
        for line in self.item_ids:
            line.state = 'waiting'

    def action_confirm(self):
        stock_quant = self.env['stock.picking.type'].search([("internal", "=", True)], limit=1)

        if not stock_quant:
            raise ValidationError(
                _("There is no stock transfer picking type"))
        self.picking_type_id = stock_quant.id
        vals = {
            "partner_id": self.user_id.partner_id.id,
            "scheduled_date": self.scheduled_date,
            "date": self.date,
            "picking_type_id": self.picking_type_id.id,
            "user_id": self.write_uid.id,
            "origin": self.name,
            "state": 'draft',
            "stock_request": self.id,
            "location_id": self.picking_type_id.default_location_src_id.id,
            "location_dest_id": self.picking_type_id.default_location_dest_id.id,
        }
        move_ids = []
        for line in self.item_ids:
            if line.available_in_store == True:
                operation_line_data = {
                    "product_uom_qty": line.demand,
                    "name": line.product_id.display_name,
                    "product_id": line.product_id.id,
                    "product_uom": line.product_id.uom_id.id
                }
                operation_line = (0, 0, operation_line_data)
                move_ids.append(operation_line)

        vals['move_lines'] = move_ids
        stock_picking = self.env['stock.picking'].create(vals)
        self.state = 'approved'
        for line in self.item_ids:
            line.state = 'approved'

    def action_cancel(self):
        for record in self:
            record.state = "cancel"
            record.canceled_id = self.env.user.id

    def action_draft(self):
        for record in self:
            record.state = "draft"

class PurchaseRequst(models.Model):
    _inherit = 'sprogroup.purchase.request'

    sr = fields.Many2one('transfer.request', "Stock Request")

    @api.depends('sr')
    def set_transfer_req_pr(self):
        for record in self:
            record.sr.pr = record.id


class Payment_request_item(models.Model):
    _name = "transfer.request.item"
    _description = "Transfer Request item"

    number = fields.Integer('Number', default=0, readonly=True)
    transfer_request_id = fields.Many2one('transfer.request', 'Request')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    pr = fields.Many2one('sprogroup.purchase.request', 'purchase request')
    demand = fields.Float(string="Demand", required=True)
    provide = fields.Float(string="Provide")
    returned = fields.Float(string="Returned")

    available_in_store = fields.Boolean("Available", default=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting For Approval'),
        ('approved', 'Approve'),
        ('done', 'Recieved'),
        ('return', 'Returned'),
        ('cancel', 'Cancel')

    ], string='Status',
        copy=False, index=True, readonly=True, store=True, tracking=True, default="draft")

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.product_tmpl_id.uom_id.id

    def request_purchase(self):
        req_line_prod = []
        product_qty_req = self.demand - self.provide
        data = {
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'product_qty': product_qty_req
        }
        req_line_prod.append(data)

        if self.transfer_request_id.state == 'approved' or self.transfer_request_id.state == 'return':
            view = self.env.ref('purchase_request.view_sprogroup_purchase_request_form')
            return {
                'name': _('Purchase Request'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sprogroup.purchase.request',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',

                # Pass the product and quantity to the form view as context data

                "context": {
                    'default_description': "Purchase request from transfer request",
                    'default_line_ids': req_line_prod,
                    'default_sr': self.transfer_request_id.id
                },

            }
        else:
            raise UserError("Your can not create purchase request in this stage")




class Picking(models.Model):
    _inherit = "stock.picking"

    stock_request = fields.Many2one("transfer.request", string='stock request')

    def action_done(self):
        print("action_done")
        if self.stock_request:
            if self.origin:
                origin = str(self.origin)
                all_word = origin.split()
                first_word = all_word[0]
                if first_word == 'Return':
                    self.stock_request.state = 'return'
                    for line in self.move_ids_without_package:
                        for line2 in self.stock_request.item_ids:
                            print("line.product_id.id == line2.product_id.id", line.product_id.id, line2.product_id.id)
                            if line.product_id.id == line2.product_id.id:
                                line2.returned = line.quantity_done
                else:
                    self.stock_request.state = 'done'
                    for line in self.move_ids_without_package:
                        for line2 in self.stock_request.item_ids:
                            if line.product_id.id == line2.product_id.id:
                                line2.provide = line.quantity_done


            else:
                self.stock_request.state = 'done'
                for line in self.move_ids_without_package:
                    for line2 in self.stock_request.item_ids:

                        if line.product_id.id == line2.product_id.id:
                            line2.provide = line.quantity_done

        return super(Picking, self).action_done()


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    internal = fields.Boolean(
        'Is internal transfer operation', default=False)


class Employee(models.Model):
    _inherit = "hr.employee"

    invoice_count_3 = fields.Integer(
        compute="_compute_count_invoice_3", string="expanse Count")
    Employee_material_count = fields.Integer(String="employee material count",help="field for graph view")

    def _compute_count_invoice_3(self):
        obj = self.env['transfer.request']
        for serv in self:
            serv.invoice_count_3 = obj.search_count([('received_id', '=', self.id),('asset','=', True)])
            serv.Employee_material_count = serv.invoice_count_3
        print("serv.invoice_count", serv.invoice_count_3)


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        print("_create_returns")
        active_id = self.env.context.get('active_id')
        rules = self.env['stock.picking'].search([('id', '=', active_id)])
        for rule in rules:
            if rule.stock_request:
                rule.stock_request.state = 'return'

        return super(ReturnPicking, self)._create_returns()
