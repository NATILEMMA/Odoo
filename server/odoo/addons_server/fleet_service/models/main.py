from collections import defaultdict
from distutils.log import error
from itertools import groupby
from re import search

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import float_is_zero, OrderedSet
from datetime import timedelta
from datetime import datetime, time
from odoo.tools import ustr

import logging

_logger = logging.getLogger(__name__)


class Fleet_service(models.Model):
    _name = "fleet.service"

    # invoice_count_3 = fields.Integer(
    #     compute="_compute_count_invoice_3", string="expanse Count")
    # invoice_count_2 = fields.Integer(
    #     compute="_compute_count_invoice_2", string="purchase Count")
    #
    # def _compute_count_invoice_3(self):
    #     obj = self.env['hr.expense']
    #     for serv in self:
    #         serv.invoice_count = obj.search_count([('services', '=', self.id)])
    #
    # def _compute_count_invoice_2(self):
    #     obj = self.env['purchase.order.line']
    #     for serv in self:
    #         serv.invoice_count_2 = obj.search_count([('services', '=', self.id)])


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")




class Expense_Update(models.Model):
    _inherit = "hr.expense"
    vehicle_select = fields.Boolean("Select Vehicle")
    is_services = fields.Boolean("is_services")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    services = fields.Many2one('fleet.vehicle.log.services', string="services")
    is_vehicle_service = fields.Boolean("Is Vehicle Service")


class Fleet_Service_Update(models.Model):
    _inherit = "fleet.vehicle.log.services"

    

    payment_count = fields.Integer("Payment Count")
    analytic = fields.Many2one('account.analytic.account', string="Analytic Account", requied=True, options={'no_create': True, 'no_edit': True, 'no_open': True})
    invoice_count = fields.Integer(
        compute="_compute_count_invoice", string="expanse Count")
    invoice_count_2 = fields.Integer(
        compute="_compute_count_invoice_2", string="purchase Count")

    def _compute_count_invoice(self):
        obj = self.env['hr.expense']
        for serv in self:
            serv.invoice_count = obj.search_count([('services', '=', self.id)])

    def _compute_count_invoice_2(self):
        obj = self.env['purchase.order.line']
        for serv in self:
            serv.invoice_count_2 = obj.search_count([('services', '=', self.id)])

    def action_create_payment(self):
        fleet = self.env['product.product'].search([('default_code', '=', 'Fleet_product_1')],limit=1)
        if not fleet: 
           raise ValidationError("The fleet product is not found! Reinstall fleet_operation module!!! ")
        """Invoice for Deposit Receive."""
        if self.state == 'approved':
            for service in self:
                exp_values = {
                    'name': self.seq or 'services',
                    'unit_amount': service.service_amount,
                    'date': service.date,
                    'product_id':fleet.id,
                    'employee_id': self.env.user.employee_id.id,
                    'quantity': 1,
                    'vehicle_select': self.vechical_type_id,
                    'analytic_account_id': self.analytic.id,
                    'services': self.id,
                    'is_vehicle_service': True,
                    'vehicle_id': self.vehicle_id.id,
                    'covered_by':self.covered_by


                }
                for rec in service.repair_line_ids:
                    rec.is_invoiced = True
                print('exp_values', exp_values)
                self.env['hr.expense'].create(exp_values)
                old = service.service_amount
                self.old_price = old
                self.state = 'confirm'
                self.vehicle_id.state = 'in_progress'
                #print("self.vechical_type_id.state", self.vechical_type_id.state)

        else:
            for service in self:
                if service.additional_payment <= 0.0:
                    raise ValidationError("The services is fully paid!!")
                # elif self.wrk_attach_ids or not self.vehicle_id.driver_id:
                else:
                    exp_values = {
                        'name': self.seq,
                        'unit_amount': service.additional_payment,
                        'date': service.date,
                        'product_id': fleet.id,
                        'employee_id': self.env.user.employee_id.id,
                        'analytic_account_id': 1,
                        'is_vehicle_service': True,
                        'is_services': True,
                        'quantity': 1,
                        'vehicle_select': self.vechical_type_id,
                        'analytic_account_id': self.analytic.id,
                        'services': self.id,
                        'vehicle_id': self.vehicle_id.id,
                        'covered_by':self.covered_by

                    }
                    self.env['hr.expense'].create(exp_values)
                    old = service.service_amount
                    service.additional_payment = 0
                    self.state = 'confirm'
                    self.vehicle_id.state = 'in_progress'


                    for rec in service.repair_line_ids:
                        rec.is_invoiced = True




