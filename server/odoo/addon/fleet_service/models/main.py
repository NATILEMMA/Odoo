from collections import defaultdict
from distutils.log import error
from itertools import groupby
from re import search

from odoo import api, fields, models,  SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError,Warning
from odoo.tools import float_is_zero, OrderedSet
from datetime import timedelta
from datetime import datetime , time
from odoo.tools import ustr

import logging
_logger = logging.getLogger(__name__)



class Fleet_service(models.Model):
    _name = "fleet.service"

class Expense_Update(models.Model):
    _inherit="hr.expense"
    vehicle_select =fields.Boolean("Select Vehicle")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    is_vehicle_service = fields.Boolean("Is Vehicle Service")

class Fleet_Service_Update(models.Model):
    _inherit="fleet.vehicle.log.services"

    # state = fields.Selection([
    #     ('draft', 'New'),
    #     ('requested', 'Requested'),
    #     ('approved', 'Approved'),
    #     ('confirm', 'Open'),
    #     ('done', 'Done'),
    #     ('cancel', 'Cancel')], string='Status',
    #     default='draft', readonly=True, tracking=True)

    payment_count = fields.Integer("Payment Count")
    invoice_count = fields.Integer(
        compute="_compute_count_invoice", string="Invoice Count")

    def _compute_count_invoice(self):
        obj = self.env['hr.expense']
        for serv in self:
            serv.invoice_count = obj.search_count([('is_vehicle_service','=',True)])

    def action_create_payment(self):
        """Invoice for Deposit Receive."""
        # moves = self.env['account.move'].search([('name', '=', "services")]

        # num = 0
        # for move in moves:
        #     num = num + 1
        #     move.name = "SER/2022/00000" + str(num)
        if self.state == 'approved':
            for service in self:
                if service.service_amount <= 0.0:
                    raise ValidationError("You can not create payment  without amount!!"
                                          "Please add Service amount first !!")
                # elif self.wrk_attach_ids or not self.vehicle_id.driver_id:
                else:
                    # deposit_inv_ids = self.env['account.move'].search([
                    #     ('vehicle_service_id', '=', service.id), ('type', '=', 'out_invoice'),
                    #     ('state', 'in', ['draft', 'open', 'in_payment'])
                    # ])
                    # if deposit_inv_ids:
                    #     raise Warning(_("Deposit invoice is already Pending\n"
                    #                     "Please proceed that deposit invoice first"))

                    if not service.purchaser_id:
                        if not service.purchaser_id2:
                            raise Warning(
                                _("Please configure Driver from vehicle or in a service order!!"))

                    if not self.pre_main:
                        inv_ser_line = [(0, 0, {
                            'name': ustr(service.cost_subtype_id and
                                         service.cost_subtype_id.name) + ' - Service Cost',
                            'price_unit': service.amount2 - service.out_amount,
                            'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                                          service.vehicle_id.income_acc_id.id or False,
                        }),
                                        (0, 0, {
                            'name': ustr(service.cost_subtype_id and
                                         service.cost_subtype_id.name) + ' - out source Cost',
                            'price_unit': service.out_amount,
                            'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                                          service.vehicle_id.income_acc_id.id or False,
                        })]
                    else:

                        inv_ser_line = [(0, 0, {
                            'name': service.pre_name + ' - Service Cost',
                            'price_unit': service.amount2 - service.out_amount,
                            'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                                          service.vehicle_id.income_acc_id.id or False,
                        }),
                            (0, 0, {
                            'name': service.pre_name + ' - Out source Cost',
                            'price_unit': service.out_amount,
                            'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                                          service.vehicle_id.income_acc_id.id or False,
                        })]

                    for line in service.parts_ids:
                            inv_line_values = {
                                'product_id': line.product_id and
                                              line.product_id.id or False,
                                'name': line.product_id and
                                        line.product_id.name or '',
                                'price_unit': line.price_unit or 0.00,
                                'quantity': line.qty,
                                'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                                              service.vehicle_id.income_acc_id.id or False
                            }
                            inv_ser_line.append((0, 0, inv_line_values))

                            service.parts_ids.is_invoice = True
                    _logger.info("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
                    _logger.info(inv_ser_line)

                    if service.purchaser_id2.id:
                        inv_values = {
                            'partner_id': service.purchaser_id2 and
                                          service.purchaser_id2.id or False,
                            'name': self.seq or 'services',
                            'ref': self.seq,
                            'type': 'out_invoice',
                            'journal_id':1,
                            'invoice_date': service.date_open,
                            'invoice_date_due': service.date_complete,
                            'invoice_line_ids': inv_ser_line,
                            'vehicle_service_id': service.id,
                            'is_invoice_receive': True,
                            'is_vehicle_service':True

                            # 'att2': self.wrk_attach_ids.id
                        }
                        exp_values = {
                            'name': self.seq or 'services',
                            # 'journal_id':1,
                            'unit_amount':service.service_amount,
                            'date': service.date,
                            'product_id': 2,
                            'employee_id':1,
                            'analytic_account_id':1,
                            'is_vehicle_service':True,
                            

                        }
                    else:
                        inv_values = {
                            'name': self.seq or 'services',
                            'partner_id': service.purchaser_id and
                                          service.purchaser_id.partner_id or False,
                            'ref': self.seq or 'services',
                            'journal_id':1,
                            'type': 'out_invoice',
                            'invoice_date': service.date_open,
                            'invoice_date_due': service.date_complete,
                            'invoice_line_ids': inv_ser_line,
                            'vehicle_service_id': service.id,
                            'is_invoice_receive': True,
                            'is_vehicle_service':True
                        }
                        exp_values = {
                            'name': self.seq or 'services',
                            # 'journal_id':1,
                            'unit_amount':service.service_amount,
                            'date': service.date,
                            'product_id': 2,
                            'employee_id':1,
                            'analytic_account_id':1,
                            'is_vehicle_service':True

                        }
                    for rec in service.repair_line_ids:
                        rec.is_invoiced = True
                    # self.env['account.move'].create(inv_values)
                    self.env['hr.expense'].create(exp_values)

                    old = self.amount2
                    self.old_price = old
                    old_part = self.sub_total
                    self.old_part_price = old_part
                    self.state = 'done'

                # else:
                #     raise Warning(
                #         _("Please attach payment slip"))
        else:
            for service in self:
                if service.additional_payment <= 0.0:
                    raise ValidationError("The services is fully paid!!")
                # elif self.wrk_attach_ids or not self.vehicle_id.driver_id:
                else:
                    deposit_inv_ids = self.env['account.move'].search([
                        ('vehicle_service_id', '=', service.id), ('type', '=', 'out_invoice'),
                        ('state', 'in', ['draft', 'open', 'in_payment'])
                    ])

                    if not service.purchaser_id:
                        if not service.purchaser_id2:
                            raise Warning(
                                _("Please configure Driver from vehicle or in a service order!!"))
                    if not self.pre_main:
                        inv_ser_line = [(0, 0, {
                            'name': ustr(service.cost_subtype_id and
                                         service.cost_subtype_id.name) + ' - Service Cost',
                            'price_unit': service.additional_service,
                            'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                                          service.vehicle_id.income_acc_id.id or False,
                        })]
                    else:
                        inv_ser_line = [(0, 0, {
                            'name': service.pre_name + ' - Service Cost',
                            'price_unit': service.additional_service,
                            'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                                          service.vehicle_id.income_acc_id.id or False,
                        })]
                    for line in service.parts_ids:
                        print("line.is_invoice", line.is_invoice)
                        if not line.is_invoice:
                            inv_line_values = {
                                'product_id': line.product_id and
                                              line.product_id.id or False,
                                'name': line.product_id and
                                        line.product_id.name or '',
                                'price_unit': line.price_unit or 0.00,
                                'quantity': line.qty,
                                'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                                              service.vehicle_id.income_acc_id.id or False
                            }
                            inv_ser_line.append((0, 0, inv_line_values))
                    _logger.info("0000000000000000000000000000000000000000000000000000000000000")
                    _logger.info(inv_ser_line)
                    service.parts_ids.is_invoice = True
                    service.repair_line_ids.is_invoiced = True


                    if service.purchaser_id2.id:
                        inv_values = {
                            'partner_id': service.purchaser_id2 and
                                          service.purchaser_id2.id or False,
                            'name': self.seq or 'services',
                            'ref': self.seq,
                            'journal_id':1,
                            'type': 'out_invoice',
                            'invoice_date': service.date_open,
                            'invoice_date_due': service.date_complete,
                            'invoice_line_ids': inv_ser_line,
                            'vehicle_service_id': service.id,
                            'is_invoice_receive': True,
                            # 'att2': self.wrk_attach_ids.id
                        }
                        exp_values = {
                            'name': self.seq,
                            'unit_amount':service.service_amount,
                            # 'journal_id':1,
                            'date': service.date,
                            'product_id': 2,
                            'employee_id':1,
                            'analytic_account_id':1,
                            'is_vehicle_service':True

                        }


                    else:
                        inv_values = {
                            'partner_id': service.purchaser_id and
                                          service.purchaser_id.partner_id or False,
                            'ref': self.seq ,
                            'type': 'out_invoice',
                            'journal_id':1,
                            'invoice_date': service.date_open,
                            'invoice_date_due': service.date_complete,
                            'invoice_line_ids': inv_ser_line,
                            'vehicle_service_id': service.id,
                            'is_invoice_receive': True,
                            'is_vehicle_service':True
                        }
                        exp_values = {
                            'name': self.seq,
                            # 'journal_id':1,
                            'unit_amount':service.service_amount,
                            'date': service.date,
                            'product_id': 2,
                            'employee_id':1,
                            'analytic_account_id':1,
                            'is_vehicle_service':True

                        }
                    # self.env['account.move'].create(inv_values)
                    self.env['hr.expense'].create(exp_values)

                    old = self.amount2
                    self.old_price = old
                    old_part = self.sub_total
                    self.old_part_price = old_part
                    self.additional_payment = 0
                    self.additional_service = 0
                    self.additional_part = 0
                    for rec in service.repair_line_ids:
                        rec.is_invoiced = True
                # else:
                #     raise Warning(
                #         _("Please attach payment slip"))

