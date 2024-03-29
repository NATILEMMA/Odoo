# See LICENSE file for full copyright and licensing details.
"""Fleet Service model."""
import time
from datetime import date, datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, misc, ustr
from odoo.tools.float_utils import float_compare

import logging

_logger = logging.getLogger(__name__)


class ServiceCategory(models.Model):
    """Service Category Model."""

    _name = 'service.category'
    _description = 'Vehicle Service Category'

    name = fields.Char(string="Service Category", translate=True)

class HrFleet(models.Model):
    """hr expense inherit ."""

    _inherit = 'hr.expense'


    covered_by = fields.Selection([('insurance','Insurance'),('company','Company')],string="Covered by",default='company')

class FleetVehicleLogServices(models.Model):
    """Fleet Vehicle Log Services Model."""

    _inherit = 'fleet.vehicle.log.services'
    _order = 'id desc'
    _rec_name = 'name'

    covered_by = fields.Selection([('insurance','Insurance'),('company','Company')],string="Covered by",default='company')

    def unlink(self):
        """Unlink Method."""
        for rec in self:
            if rec.state != 'draft':
                raise Warning(_('You can\'t delete Work Order which '
                                'in Confirmed or Done state!'))
        return super(FleetVehicleLogServices, self).unlink()

    @api.depends('amount2')
    def get_amount(self):
        print("@api.onchange('amount')")
        for rec in self:
            for line in self.repair_line_ids:
                if line.estimated_time > 0:
                        total_price = total_price + line.price
                else:
                        total_price = total_price + line.price
                rec.amount = total_price

    @api.onchange('repair_line_ids')
    def get_prices(self):
        total_price = 0
        total_price_2 = 0
        self.additional_payment = 0
        for rec in self:
            for line in self.repair_line_ids:
                if line.estimated_time > 0:
                    total_price = total_price + line.price
                else:
                    total_price = total_price + line.price
                if line.is_source:
                    total_price_2 = total_price_2 + line.price
            rec.out_amount = total_price_2
            rec.amount2 = total_price
            rec.service_amount = rec.sub_total + rec.amount2
            if str(rec.state) != 'approved':
               print("if str(rec.state) != 'aprroved':")
               if rec.service_amount != rec.old_price:
                 if rec.service_amount - rec.old_price >= 0:
                     rec.additional_service = rec.amount2 - rec.old_price
                     rec.additional_part = rec.sub_total - rec.old_part_price
                     rec.additional_payment = rec.additional_service + rec.additional_part
                     print(rec.additional_service, rec.service_amount, rec.old_price, rec.additional_part)


    @api.onchange('vehicle_id')
    def get_vehicle_info(self):
        """Onchange Method."""
        if self.vehicle_id:
            print("self.vehicle_id", self.vehicle_id)
            print("driver_id", self.vehicle_id.driver_id)
            vehicle = self.vehicle_id
            self.vechical_type_id = vehicle.vechical_type_id and \
                                    vehicle.vechical_type_id.id or False,
            print("self.vehicle_id", self.vehicle_id.id)
            if vehicle.driver_id:
                self.purchaser_id2 = vehicle.driver_id and \
                                     vehicle.driver_id.id or False,
                print("cus", self.purchaser_id.id)
                self.is_customer = True
                print("self.is_customer", self.is_customer)
            else:
                self.purchaser_id = vehicle.vehicle_owner and \
                                    vehicle.vehicle_owner.id or False,

                self.is_customer = False


            self.f_brand_id = vehicle.f_brand_id and \
                              vehicle.f_brand_id.id or False,
            self.vehical_division_id = vehicle.vehical_division_id and \
                                       vehicle.vehical_division_id.id or False,
            self.vehicle_location_id = vehicle.vehicle_location_id and \
                                       vehicle.vehicle_location_id.id or False,

    def compute(self):
        moves = self.env['account.move'].search([('name', '=', "services")])
        fleet = self.env['fleet.vehicle.log.services'].search([('name', '=', False)])
        num = 0
        for move in moves:
            num = num + 1
            move.name = "SER/2022/0000" + str(num)
        for flee in fleet:
            num = num + 1
            flee.name = "SER/2022/0000" + str(num)

    def set_approved(self):
        self.state = 'approved'
        moves = self.env['account.move'].search([
                ('type', '=', 'out_invoice'),
                ('vehicle_service_id', '=', self.id)])
        for line in moves:
            if line.state == 'posted':
                raise ValidationError("You can not change severe if the invoice posted")
            else:
                line.state = 'cancel'
                self.state = 'approved'

    def action_create_invoice(self):
        """Invoice for Deposit Receive."""
        moves = self.env['account.move'].search([('name', '=', "services")])
        num = 0
        for move in moves:
            num = num + 1
            move.name = "SER/2022/00000" + str(num)
        if self.state == 'approved':
            for service in self:
                if service.service_amount <= 0.0:
                    raise ValidationError("You can not create service invoice without amount!!"
                                          "Please add Service amount first !!")
                elif self.wrk_attach_ids or not self.vehicle_id.driver_id:
                    deposit_inv_ids = self.env['account.move'].search([
                        ('vehicle_service_id', '=', service.id), ('type', '=', 'out_invoice'),
                        ('state', 'in', ['draft', 'open', 'in_payment'])
                    ])
                    if deposit_inv_ids:
                        raise Warning(_("Deposit invoice is already Pending\n"
                                        "Please proceed that deposit invoice first"))

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
                            'att2': self.wrk_attach_ids.id
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
                        }
                    for rec in service.repair_line_ids:
                        rec.is_invoiced = True
                    self.env['account.move'].create(inv_values)
                    old = self.amount2
                    self.old_price = old
                    old_part = self.sub_total
                    self.old_part_price = old_part
                    self.state = 'invoice'

                else:
                    raise Warning(
                        _("Please attach payment slip"))
        else:
            for service in self:
                if service.additional_payment <= 0.0:
                    raise ValidationError("The services is fully paid!!")
                elif self.wrk_attach_ids or not self.vehicle_id.driver_id:
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
                            'att2': self.wrk_attach_ids.id
                        }
                    else:
                        inv_values = {
                            'partner_id': service.purchaser_id and
                                          service.purchaser_id.partner_id or False,
                            'ref': self.seq,
                            'type': 'out_invoice',
                            'journal_id':1,
                            'invoice_date': service.date_open,
                            'invoice_date_due': service.date_complete,
                            'invoice_line_ids': inv_ser_line,
                            'vehicle_service_id': service.id,
                            'is_invoice_receive': True,
                        }
                    self.env['account.move'].create(inv_values)
                    old = self.amount2
                    self.old_price = old
                    old_part = self.sub_total
                    self.old_part_price = old_part
                    self.additional_payment = 0
                    self.additional_service = 0
                    self.additional_part = 0
                    for rec in service.repair_line_ids:
                        rec.is_invoiced = True
                else:
                    raise Warning(
                        _("Please attach payment slip"))

    def action_return_invoice(self):
        """Invoice for Deposit Return."""

        for service in self:
            deposit_inv_ids = self.env['account.move'].search([
                ('vehicle_service_id', '=', service.id), ('type', '=', 'out_refund'),
                ('state', 'in', ['draft', 'open', 'in_payment'])
            ])
            if deposit_inv_ids:
                raise Warning(_("Deposit Return invoice is already Pending\n"
                                "Please proceed that deposit invoice first"))

            inv_ser_line = [(0, 0, {
                'product_id': service.cost_subtype_id and
                              service.cost_subtype_id.id or False,
                'name': 'Service Cost',
                'price_unit': service.amount2 or 0.0,
                'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                              service.vehicle_id.income_acc_id.id or False,
            })]
            parts = self.env['task.line'].search([
                ('fleet_service_id', '=', service.id),
                ('is_invoice', '=', False)])
            for line in parts:
                inv_line_values = {
                    'product_id': line.product_id.id or False,
                    'name': 'Service Cost',
                    'price_unit': line.price_unit or 0.00,
                    'quantity': line.qty,
                    'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                                  service.vehicle_id.income_acc_id.id or False
                }
                inv_ser_line.append((0, 0, inv_line_values))
                parts.is_invoice = True

            inv_values = {
                'partner_id': service.purchaser_id and
                              service.purchaser_id.id or False,
                'type': 'out_refund',
                'invoice_date': service.date_open,
                'invoice_date_due': service.date_complete,
                'invoice_line_ids': inv_ser_line,
                'vehicle_service_id': service.id,
                'is_invoice_return': True,
            }
            self.env['account.move'].create(inv_values)

    def submit_request(self):
        self.state = 'requested'
        return

    def approve_request(self):
        sequence = self.env['ir.sequence'].next_by_code(
            'service.order.sequence')
        self.seq = sequence
        self.name = sequence
        self.state = 'confirm'
        self.vehicle_id.state = 'in_progress'
        return

    def action_cancel(self):
        self.state = 'invoice'
        return

    def approve_denied(self):
        self.state = 'cancel'
        return

    def action_confirm(self):
        """Action Confirm Of Button."""
        if self.wrk_attach_ids or not self.vehicle_id.driver_id:
            sequence = self.seq
            mod_obj = self.env['ir.model.data']
            context = self.env.context.copy()
            for work_order in self:
                if work_order.vehicle_id:
                    if work_order.vehicle_id.state == 'write-off':
                        raise Warning(_("You can\'t confirm this \
                                work order which vehicle is in write-off state!"))
                    elif work_order.vehicle_id.state == 'in_progress':
                        raise Warning(_("Previous work order is not "
                                        "complete, complete that work order first than "
                                        "you can confirm this work order!"))
                    elif work_order.vehicle_id.state == 'draft' or \
                            work_order.vehicle_id.state == 'complete':
                        raise Warning(_("Confirm work order can only "
                                        "when vehicle status is in Inspection or Released!"))
                    work_order.vehicle_id.write({
                        'state': 'in_progress',
                        'last_change_status_date': date.today(),
                        'work_order_close': False})
                work_order.write({'state': 'confirm', 'name': sequence,
                                  'date_open':
                                      time.strftime(DEFAULT_SERVER_DATE_FORMAT)})
                model_data_ids = mod_obj.search([
                    ('model', '=', 'ir.ui.view'),
                    ('name', '=', 'continue_pending_repair_form_view')])
                resource_id = model_data_ids.read(['res_id'])[0]['res_id']
                context.update({'work_order_id': work_order.id,
                                'vehicle_id': work_order.vehicle_id and
                                              work_order.vehicle_id.id or False})
                if work_order.vehicle_id:
                    for pending_repair in \
                            work_order.vehicle_id.pending_repair_type_ids:
                        if pending_repair.state == 'in-complete':
                            return {
                                'name': _('Previous Repair Types'),
                                'context': context,
                                'view_type': 'form',
                                'view_mode': 'form',
                                'res_model': 'continue.pending.repair',
                                'views': [(resource_id, 'form')],
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                            }
            self.repair_line_ids.state = 'confirm'
            return True
        else:
            raise Warning(_("please attach payment slip"))

    def action_done(self):
      if self.additional_payment ==0 :
        for check in self.repair_line_ids:
            if not check.complete:
                raise ValidationError('The task are not completed')
            else:
                context2 = self._context
                current_uid = context2.get('uid')
                check.approve = current_uid
        context = dict(self.env.context)
        odometer_increment = 0.0
        increment_obj = self.env['next.increment.number']
        next_service_day_obj = self.env['next.service.days']
        mod_obj = self.env['ir.model.data']
        for work_order in self:
            service_inv = self.env['account.move'].search([
                ('type', '=', 'out_invoice'),
                ('vehicle_service_id', '=', work_order.id)])
            # if work_order.amount2 > 0 and not service_inv:
            #     raise ValidationError("Vehicle Service amount is greater"
            #                           " than Zero So, "
            #                           "Without Service Invoice you can not done the Service !!" "Please Generate Service Invoice first !!")

            for repair_line in work_order.repair_line_ids:
                if repair_line.complete is True:
                    continue
                elif repair_line.complete is False:
                    model_data_ids = mod_obj.search([
                        ('model', '=', 'ir.ui.view'),
                        ('name', '=', 'pending_repair_confirm_form_view')])
                    resource_id = model_data_ids.read(['res_id'])[0]['res_id']
                    context.update({'work_order_id': work_order.id})
                    # self.env.args = cr, uid, misc.frozendict(context)
                    return {
                        'name': _('WO Close Forcefully'),
                        'context': context,
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'pending.repair.confirm',
                        'views': [(resource_id, 'form')],
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }

        increment_ids = increment_obj.search([
            ('vehicle_id', '=', work_order.vehicle_id.id)])
        if not increment_ids:
            return {
                'name': _('Next Service Day'),
                'res_model': 'update.next.service.config',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'
            }
        if increment_ids:
            odometer_increment = increment_ids[0].number

        next_service_day_ids = next_service_day_obj.search([
            ('vehicle_id', '=', work_order.vehicle_id.id)])
        if not next_service_day_ids:
            return {
                'name': _('Next Service Day'),
                'res_model': 'update.next.service.config',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'
            }
        work_order_vals = {}
        for work_order in self:
            # self.env.args = cr, uid, misc.frozendict(context)
            user = self.env.user
            if work_order.odometer == 0:
                raise Warning(_("Please set the current "
                                "Odometer of vehicle in work order!"))
            odometer_increment += work_order.odometer
            next_service_date = datetime.strptime(
                str(date.today()), DEFAULT_SERVER_DATE_FORMAT) + \
                                timedelta(days=next_service_day_ids[0].days)
            work_order_vals.update({
                'state': 'done',
                'next_service_odometer': odometer_increment,
                'already_closed': True,
                'closed_by': user,
                'date_close': fields.Date.today(),
                'next_service_date': next_service_date})
            work_order.write(work_order_vals)
            if work_order.vehicle_id:
                work_order.vehicle_id.write({
                    'state': 'complete',
                    'last_service_by_id': work_order.team_id and
                                          work_order.team_id.id or False,
                    'last_service_date': fields.Date.today(),
                    'next_service_date': next_service_date,
                    'due_odometer': odometer_increment,
                    'due_odometer_unit': work_order.odometer_unit,
                    'last_change_status_date': fields.Date.today(),
                    'work_order_close': True})
                if work_order.already_closed:
                    for repair_line in work_order.repair_line_ids:
                        for pending_repair_line in \
                                work_order.vehicle_id.pending_repair_type_ids:
                            if repair_line.repair_type_id.id == \
                                    pending_repair_line.repair_type_id.id and \
                                    work_order.name == \
                                    pending_repair_line.name:
                                if repair_line.complete is True:
                                    pending_repair_line.unlink()
        ######## commenting the stock create part
        # if work_order.parts_ids:
        #     parts = self.env['task.line'].search([
        #         ('fleet_service_id', '=', work_order.id),
        #         ('is_deliver', '=', False)])
        #     user = self.env.user
        #     print("user", user)
        #     for loc in user:
        #         4 = self.env['stock.warehouse'].search([('operating_unit_id', '=', user.default_operating_unit_id.id)])
        #     for ware in warehouse:
        #          self.location_id = ware.lot_stock_id.id
        #          self.picking_type_id = ware.out_type_id.id
        #          print("ware.out_type_id.id", ware.out_type_id.id)
        #     if parts:
                picking = {

                    'partner_id': self.vehicle_id.driver_id.id,
                    'state': 'confirmed',
                    'show_check_availability': True,
                    'origin': self.name,
                    'location_dest_id': self.vehicle_id.driver_id.property_stock_customer.id or False,
                    'location_id': self.location_id.id,
                    'picking_type_id': self.picking_type_id.id,
                    'move_line_ids_without_package': [],
                    'move_ids_without_package': [],
                }
                # for part in parts:
                #     part.write({'is_deliver': True})
                    #source_location = self.env.ref(
                    #'stock.picking_type_out').default_location_src_id
                    #dest_location, loc = self.env['stock.warehouse']._get_partner_locations()
                    # move = self.env['stock.move'].create({
                    #     'name': 'Used in Work Order',
                    #     'product_id': part.product_id.id or False,
                    #     'location_id': part.product_id.property_stock_inventory.id or False,
                    #     'location_dest_id': self.vehicle_id.driver_id.property_stock_customer.id or self.vehicle_id.vehicle_owner.property_stock_customer.id or False,
                    #     'product_uom': part.product_uom.id or False,
                    #     'product_uom_qty': part.qty or 0.0
                    # })
                    # move._action_confirm()
                    # move._action_assign()
                    # move.move_line_ids.write({'qty_done': part.qty})
                    # move._action_done()
                #     picking['move_ids_without_package'].append(
                #         (0, 0, {
                #             'name': 'ser',
                #             'product_id': part.product_id.id or False,
                #             'product_uom_qty': part.qty or 0.0,
                #             'reserved_availability': part.qty or 0.0,
                #             'state': 'assigned',
                #             'product_uom': part.product_uom.id or False,
                #             'location_dest_id': self.vehicle_id.driver_id.property_stock_customer.id or False,
                #             'location_id': self.location_id.id,
                #             'picking_type_id': self.picking_type_id.id,
                #             # 'origin': self.name,
                #
                #         }))
                #     picking['move_line_ids_without_package'].append(
                #         (0, 0, {
                #             'product_id': part.product_id.id or False,
                #             'product_uom_qty': part.product_uom.id or False,
                #             'product_uom_id': part.product_uom.id or False,
                #             'location_id': self.location_id.id,
                #             'location_dest_id': self.vehicle_id.driver_id.property_stock_customer.id or False,
                #         }))
                # # move = self.env['stock.picking'].sudo().create(picking)
                # move.state = 'confirmed'
        return True
      else:
          raise ValidationError('There are unpaid amount')
    def encode_history(self):
        """Method is used to create the Encode Qty.

        History for Team Trip from WO.
        """
        wo_part_his_obj = self.env['workorder.parts.history.details']
        if self._context.get('team_trip', False):
            team_trip = self._context.get('team_trip', False)
            work_order = self._context.get('workorder', False)
            # If existing parts Updated
            wo_part_his_ids = wo_part_his_obj.search([
                ('team_id', '=', team_trip and team_trip.id or False),
                ('wo_id', '=', work_order and work_order.id or False)])
            if wo_part_his_ids:
                wo_part_his_ids.unlink()
            wo_part_dict = {}
            for part in work_order.parts_ids:
                wo_part_dict[part.product_id.id] = \
                    {'wo_en_qty': part.encoded_qty, 'qty': part.qty}
            for t_part in team_trip.allocate_part_ids:
                if t_part.product_id.id in wo_part_dict.keys():
                    new_wo_encode_qty = \
                        wo_part_dict[t_part.product_id.id]['wo_en_qty'] - \
                        wo_part_dict[t_part.product_id.id]['qty']
                    wo_part_history_vals = {
                        'team_id': team_trip.id,
                        'product_id': t_part.product_id.id,
                        'name': t_part.product_id.name,
                        'vehicle_make': t_part.product_id.vehicle_make_id.id,
                        'used_qty': wo_part_dict[t_part.product_id.id]['qty'],
                        'wo_encoded_qty':
                            wo_part_dict[t_part.product_id.id]['wo_en_qty'],
                        'new_encode_qty': new_wo_encode_qty,
                        'wo_id': work_order.id,
                        'used_date': t_part.issue_date,
                        'issued_by': self._uid or False
                    }
                    wo_part_his_obj.create(wo_part_history_vals)
                    t_part.write({'encode_qty': new_wo_encode_qty})
        return True

    def action_reopen(self):
        """Method Action Reopen."""
        for order in self:
            order.write({'state': 'done'})
            new_reopen_service = order.copy()
            new_reopen_service.write({
                'source_service_id': order.id,
                'date_open': False,
                'date_close': False,
                'cost_subtype_id': False,
                'amount': False,
                'team_id': False,
                'closed_by': False,
                'repair_line_ids': [(6, 0, [])],
                'parts_ids': [(6, 0, [])],
            })
            return {
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'fleet.vehicle.log.services',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': new_reopen_service.id,
            }

    @api.depends('parts_ids')
    def _compute_get_total(self):
        for rec in self:
            sum2 = 0.0
            rec.additional_payment = 0
            for line in rec.parts_ids:
                line.total = line.qty * line.price_unit
                sum2 += line.qty
            rec.total_parts_line = sum2
            rec.sub_total = sum(line.total for line in self.parts_ids) or 0.0
            rec.service_amount = rec.sub_total + rec.amount2
            # print("self.state", self.state, "old_price", self.old_price, "self.service_amount",self.service_amount)
            if rec.state == 'invoice' or 'confirm':
               if rec.service_amount != rec.old_price and rec.old_price != 0:
                   if rec.sub_total - rec.old_part_price >= 0:
                    rec.additional_part = rec.sub_total - rec.old_part_price
                    rec.additional_service = rec.amount2 - rec.old_price
                    rec.additional_payment = rec.additional_part + rec.additional_service




    def write(self, vals):
        """Method Write."""
        if not self._context:
            self._context = {}
        for work_order in self:
            if work_order.vehicle_id:


                vals.update(
                    {

                        'fmp_id': work_order.vehicle_id and
                                  work_order.vehicle_id.name or "",
                        'model_id': work_order.model_id and
                                    work_order.model_id.id or "",
                        'vechical_type_id': work_order.vehicle_id and
                                            work_order.vehicle_id.vechical_type_id and
                                            work_order.vehicle_id.vechical_type_id.id or False,
                        'purchaser_id': work_order.vehicle_id and
                                        work_order.vehicle_id.driver_id and
                                        work_order.vehicle_id.driver_id.id or False,
                        'main_type': work_order.vehicle_id.main_type,
                        'f_brand_id': work_order.vehicle_id and
                                      work_order.vehicle_id.f_brand_id and
                                      work_order.vehicle_id.f_brand_id.id or False,
                        'vehical_division_id': work_order.vehicle_id and
                                               work_order.vehicle_id.vehical_division_id and
                                               work_order.vehicle_id.vehical_division_id.id or False,
                        # 'vehicle_location_id': work_order.vehicle_id and
                        # work_order.vehicle_id.vehicle_location_id and
                        # work_order.vehicle_id.vehicle_location_id.id or False,
                    })
        print(work_order.amount)
        print("edit logser",vals)
        return super(FleetVehicleLogServices, self).write(vals)


    @api.model
    def _get_location(self):
        location_id = self.env['stock.location'].search([
            ('name', '=', 'Vehicle')])
        if location_id:
            return location_id.ids[0]
        return False

    @api.model
    def default_get(self, fields):
        """Method Default get."""
        vehicle_obj = self.env['fleet.vehicle']
        repair_type_obj = self.env['repair.type']
        if self._context.get('active_ids', False):
            for vehicle in vehicle_obj.browse(self._context['active_ids']):
                if vehicle.state == 'write-off':
                    raise Warning(_("You can\'t create work order "
                                    "for vehicle which is already write-off!"))
                elif vehicle.state == 'in_progress':
                    raise Warning(_("Previous work order is not "
                                    "complete,Please complete that work order first than you "
                                    "can create new work order!"))
                elif vehicle.state == 'rent':
                    raise Warning(_("You can\'t create work order "
                                    "for vehicle which is already On Rent!"))
                elif vehicle.state == 'draft' or vehicle.state == 'complete':
                    raise Warning(_("New work order can only be "
                                    "generated either vehicle status is in "
                                    "Inspection or Released!"))
        res = super(FleetVehicleLogServices, self).default_get(fields)
        repair_type_ids = repair_type_obj.search([])
        if not repair_type_ids:
            raise Warning(_("There is no data for "
                            "repair type, add repair type from configuration!"))
        return res

    @api.onchange('cost_subtype_id')
    def get_repair_line(self):
        """Method get repair line."""
        if not self.pre_main:
            self.repair_line_ids.unlink()
            self.repair_line_ids = [(5, 0, 0)]
            repair_lines = []
            if self.cost_subtype_id:
                for repair_type in self.cost_subtype_id.repair_type_ids:
                    repair_lines.append((0, 0, {'repair_type_id': repair_type.id}))
                self.repair_line_ids = repair_lines
                for line in self.repair_line_ids:
                    id = line.repair_type_id.ids
                    repair = self.env['repair.type'].search([('id', '=', id)]).	product
                    product = self.env['product.product'].search([('id', '=', repair.id)])
                    line.estimated_time2 = product.estimated_time
                    if product.estimated_time:
                        if self.vehicle_id.vechical_type_id.price > 0:
                            payment_per_hour = self.env["res.config.settings"].search([], limit=1, order='id desc').payment_per_hour
                        else:
                            payment_per_hour = self.vehicle_id.vechical_type_id.price

                        price = payment_per_hour
                        line.price = price * product.estimated_time


    @api.onchange('checklist_template')
    def get_checklist_line(self):
        print("onchange")
        self.checklist = [(5, 0, 0)]
        checklist = []
        if self.checklist_template:
            for checklist_type in self.checklist_template.checklist:
                checklist.append((0, 0, {'checklist_id': checklist_type.id}))
            print("checklist", checklist_type)
            self.checklist = checklist

    # def _get_open_days(self):
    #     for work_order in self:
    #         diff = 0
    #         if work_order.state == 'confirm':
    #             diff = (datetime.today() -
    #                     datetime.strptime(str(work_order.date_open),
    #                                       DEFAULT_SERVER_DATE_FORMAT)).days
    #             work_order.open_days = str(diff)
    #         elif work_order.state == 'done':
    #             diff = (datetime.strptime(str(work_order.date_close),
    #                                       DEFAULT_SERVER_DATE_FORMAT) -
    #                     datetime.strptime(str(work_order.date_open),
    #                                       DEFAULT_SERVER_DATE_FORMAT)).days
    #             work_order.open_days = str(diff)
    #         else:
    #             work_order.open_days = str(diff)

    def _compute_get_total_parts_line(self):
        for work_order in self:
            work_order.total_parts_line = len([parts_line.id
                                               for parts_line in work_order.parts_ids
                                               if parts_line])

    @api.depends('repair_line_ids')
    def _compute_total_etimate_time(self):
              total = 0
              for line in self.repair_line_ids:
                  total = total + line.estimated_time2
              for ser in self:
                  ser.total_estimate_time = total

    @api.model
    def get_warehouse(self):
        """Method Get Warehouse."""
        warehouse_ids = self.env['stock.warehouse'].search([])
        if warehouse_ids:
            return warehouse_ids.ids[0]
        else:
            return False

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if not self.vehicle_id:
            return {}
        if self.vehicle_id:
            self.odometer = self.vehicle_id.odometer
            self.odometer_unit = self.vehicle_id.odometer_unit
            self.purchaser_id = self.vehicle_id.driver_id.id

    @api.constrains('date', 'date_complete')
    def check_complete_date(self):
        """Method to check complete date."""
        for vehicle in self:
            if vehicle.date and vehicle.date_complete:
                if vehicle.date_complete < vehicle.date:
                    raise ValidationError('Estimated Date Should Be '
                                          'Greater Than Issue Date.')

    checklist = fields.One2many('fleet.checklistevaluate.initial', 'service_id',
                                string='Checklist Lines')
    checklist_template = fields.Many2one('fleet.checklist.template', string='Checklist Template')
    wono_id = fields.Integer(string='WONo',
                             help="Take this field for data migration")
    id = fields.Integer(string='ID')

    purchaser_id = fields.Many2one(
        'res.users', string='Vehicle Owner', related='vehicle_id.vehicle_owner')
    purchaser_id2 = fields.Many2one(
        'res.partner', string='Customer', related='vehicle_id.driver_id')
    name = fields.Char(string='Work Order', size=32, readonly=True,
                       translate=True, copy=False, default="New")
    fmp_id = fields.Char(string="Vehicle ID", size=64,
                         related='vehicle_id.name', translate=True)
    wo_tax_amount = fields.Float(string='Tax', readonly=True)
    priority = fields.Selection([('normal', 'NORMAL'), ('high', 'HIGH'),
                                 ('low', 'LOW')], default='normal',
                                string='Work Priority')
    date_complete = fields.Date(string='Issued Complete ',
                                help='Date when the service is completed')
    date_open = fields.Date(string='Open Date',
                            help="When Work Order \
                                        will confirm this date will be set.")
    date_close = fields.Date(string='Date Close',
                             help="Closing Date of Work Order")
    closed_by = fields.Many2one('res.users', string='Closed By')
    etic = fields.Boolean(string='Estimated Time',
                          help="Estimated Time In Completion",
                          default=True, store=True)
    wrk_location_id = fields.Many2one('stock.location',
                                      string='Location ', readonly=True)
    wrk_attach_ids = fields.One2many('ir.attachment', 'wo_attachment_id',
                                     string='Attachments')
    task_ids = fields.One2many('service.task', 'main_id',
                               string='Service Task')
    parts_ids = fields.One2many('task.line', 'fleet_service_id',
                                string='Parts')
    note = fields.Text(string='Log Notes', translate=True)
    date_child = fields.Date(related='cost_id.date', string='Cost Date',
                             store=True)
    sub_total = fields.Float(compute="_compute_get_total", string='Total Parts Amount',
                             store=True)
    total_estimate_time = fields.Float(compute="_compute_total_etimate_time",
                                       string='Total Estimate time',
                                       store=True)
    out_amount = fields.Float(string='out source amount',store=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        # ('invoice', 'Paid'),
        ('confirm', 'Open'),
        ('done', 'Done'),
        # ('register', 'Register'),
        ('cancel', 'Cancel')], string='Status',
        default='draft', readonly=True, tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    delivery_id = fields.Many2one('stock.picking',
                                  string='Delivery Reference', readonly=True)
    team_id = fields.Many2one('res.partner', string="Teams")
    maintenance_team_id = fields.Many2one("stock.location", string="Team")
    next_service_date = fields.Date(string='Next Service Date')
    next_service_odometer = fields.Float(string='Next Odometer Value')
    # ,readonly=True)
    repair_line_ids = fields.One2many('service.repair.line', 'service_id',
                                      string='Repair Lines')
    old_parts_incoming_ship_ids = fields.One2many('stock.picking',
                                                  'work_order_old_id',
                                                  string='Old Returned',
                                                  readonly=True)
    reopen_return_incoming_ship_ids = fields.One2many('stock.picking',
                                                      'work_order_reopen_id',
                                                      string='Reopen Returned',
                                                      readonly=True)
    out_going_ids = fields.One2many('stock.picking', 'work_order_out_id',
                                    string='Out Going', readonly=True)
    vechical_type_id = fields.Many2one('vehicle.type', string='Vechical Type')
    # open_days = fields.Char(compute="_get_open_days", string="Open Days")
    already_closed = fields.Boolean("Already Closed?", store=True)
    total_parts_line = fields.Integer(compute="_compute_get_total_parts_line",
                                      string='Total Parts')
    is_parts = fields.Boolean(string="Is Parts Available?", store=True)
    is_customer = fields.Boolean(string="Is this services is for customer?", store=True)
    from_migration = fields.Boolean('From Migration', store=True)
    main_type = fields.Selection([('vehicle', 'Vehicle'),
                                  ('non-vehicle', ' Non-Vehicle')],
                                 string='Main Type')
    f_brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Make')
    vehical_division_id = fields.Many2one('vehicle.divison', string='Division')
    vechical_location_id = fields.Many2one(related="vehicle_id.vehicle_location_id",
                                           string='Registration State', store=True)
    odometer = fields.Float(compute='_compute_get_odometer', inverse='_compute_set_odometer',
                            string='Last Odometer',
                            help='Odometer measure of the vehicle at the \
                                moment of this log')
    service_amount = fields.Float(string="Total Service Amount", store=True)
    amount2 = fields.Float(string="Service Amount", store=True)
    source_service_id = fields.Many2one(
        'fleet.vehicle.log.services', string="Service", copy=False)
    invoice_count = fields.Integer(
        compute="_compute_count_invoice", string="Invoice Count")
    attachment_count = fields.Integer(
        compute="_compute_attachment_count", string="Attachment Count")
    return_inv_count = fields.Integer(
        compute="_compute_return_invoice", string="Return Invoice")
    amount_receive = fields.Boolean(
        compute="_compute_invoice_receive", string="Invoice Receive")
    amount_return = fields.Boolean(string="Invoice Return", store=True)
    service_invoice_id = fields.One2many('account.move', 'vehicle_service_id',
                                         string="Service Invoice")
    service_ref_invoice_id = fields.One2many('account.move', 'vehicle_service_id',
                                             string="Service Refund Invoice")
    deposit_receive = fields.Boolean(string="Deposit Received?", store=True)
    pre_main = fields.Boolean(string="Preventive maintenance?", store=True)
    model_id = fields.Many2one('fleet.vehicle.model', string='model', related='vehicle_id.model_id')
    additional_payment = fields.Float(string="Additional Payment", readonly=True,  store=True)
    invoice_amount = fields.Float(string="Invoice amount")
    additional_part = fields.Float(store=True)
    additional_service = fields.Float(store=True)
    old_price = fields.Float(store=True)
    old_part_price = fields.Float(store=True)
    seq = fields.Char(store=True, translate=True)
    pre_name = fields.Char(string="Preventive name", store=True, translate=True)
    mechanic_2 = fields.Many2one('res.users', 'Engineer', domain=[('is_mechanic', '=', True)])
    location_id = fields.Many2one('stock.location', 'Location')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type')
    account_move_id = fields.Many2one('account.move', 'Journal entry')

    @api.onchange('mechanic_2')
    def get_mechanic(self):
      if self.mechanic_2:
        for line in self.repair_line_ids:
            line.mechanic = self.mechanic_2
        return


    @api.onchange('pre_main')
    def onchange_pre_main(self):
        print("change")
        if not self.pre_main:
            self.repair_line_ids.unlink()
            self.repair_line_ids = [(5, 0, 0)]
            self.parts_ids.unlink()
            self.parts_ids = [(5, 0, 0)]
            self.pre_main = False
        else:
            terms = []
            terms_2 = []
            clause = [('vehicle_model', '=', self.model_id.id), ('service_odometer', '<=', self.odometer),('service_odometer_2', '>=', self.odometer)]
            preventive = self.env['preventive.maintenance'].search(clause, limit=1, order="service_odometer desc")
            print("preventive", preventive.maintenance_name)
            self.pre_name = preventive.maintenance_name
            print(self.pre_name)
            if self.vehicle_id.vechical_type_id.price > 0:
                payment_per_hour = self.env["res.config.settings"].search([], limit=1, order='id desc').payment_per_hour
            else:
                payment_per_hour = self.vehicle_id.vechical_type_id.price
            for pre in preventive:
                count = 0
                pre_line = self.env['preventive.maintenance.line'].search([('preventive', '=', pre.id)])


                for pre_lines in pre_line:
                    values = {}
                    values_2 = {}
                    values['repair_type_id'] = pre_lines.vehicle_model
                    values['condition'] = pre_lines.condition
                    values['type'] = pre_lines.type
                    values['estimated_time2'] = pre_lines.service_time
                    values['price'] = payment_per_hour*pre_lines.service_time
                    values['is_preventive'] = True
                    values['fmp_id'] = self.fmp_id
                    print("pre_lines.product_id", pre_lines.product_id.id)
                    if pre_lines.product_id.id != False:
                        print("pre_lines.product_id", pre_lines.product_id.id)
                        values_2['product_id'] = pre_lines.product_id
                        values_2['qty'] = 1
                        values_2['product_uom'] = 1
                        terms_2.append((0, 0, values_2))
                    terms.append((0, 0, values))


                self.repair_line_ids = terms
                self.parts_ids = terms_2



        return


    def _compute_invoice_receive(self):
        for rec in self:
            inv_obj = self.env['account.move'].search([('type', '=', 'out_invoice'),
                                                       ('vehicle_service_id', '=', rec.id), ('state', 'in',
                                                                                             ['draft', 'paid']),
                                                       ('is_invoice_receive', '=', True)])
            if inv_obj:
                rec.amount_receive = True
            else:
                rec.amount_receive = False

    def _compute_count_invoice(self):
        obj = self.env['account.move']
        for serv in self:
            serv.invoice_count = obj.search_count([
                ('type', '=', 'out_invoice'),
                ('vehicle_service_id', '=', serv.id)])

    def _compute_attachment_count(self):
        obj = self.env['ir.attachment']
        for serv in self:
            serv.attachment_count = obj.search_count([('wo_attachment_id', '=', serv.id)])


    def _compute_return_invoice(self):
        obj = self.env['account.move']
        for serv in self:
            serv.return_inv_count = obj.search_count([
                ('type', '=', 'out_refund'),
                ('vehicle_service_id', '=', serv.id)])

    @api.depends('amount2', 'sub_total')
    def _compute_total_service_amount(self):
        print("_compute_total_service_amountv")
        total_price = 0
        for rec in self:
            rec.service_amount = rec.sub_total + rec.amount2
            for line in self.repair_line_ids:
                total_price = total_price + line.price
            rec.amount2 = total_price


    def _compute_get_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search([
                ('vehicle_id', '=', record.vehicle_id.id)], limit=1,
                order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _compute_set_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search(
                [('vehicle_id', '=', record.vehicle_id.id)],
                limit=1, order='value desc')
            if record.odometer < vehicle_odometer.value:
                raise Warning(_('You can\'t enter odometer less than previous '
                                'odometer %s !') % vehicle_odometer.value)
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date,
                        'vehicle_id': record.vehicle_id.id}
                fleet_vehicle_odometer_obj.create(data)


class WorkOrderPartsHistoryDetails(models.Model):
    """Work Order Parts History Details."""

    _name = 'workorder.parts.history.details'
    _description = 'Work Order Parts History'
    _order = 'used_date desc'

    product_id = fields.Many2one('product.product', string='Part No',
                                 help='The Part Number')
    name = fields.Char(string='Part Name', help='The Part Name',
                       translate=True)
    vehicle_make = fields.Many2one('fleet.vehicle.model.brand',
                                   string='Vehicle Make',
                                   help='The Make of the Vehicle')
    used_qty = fields.Float(string='Encoded Qty',
                            help='The Quantity that is used in in Workorder')
    wo_encoded_qty = fields.Float(string='Qty',
                                  help='The Quantity which is \
                                  available to use')
    new_encode_qty = fields.Float(string='Qty for Encoding',
                                  help='New Encoded Qty')
    wo_id = fields.Many2one('fleet.vehicle.log.services', string='Workorder',
                            help='The workorder for which the part was used')
    used_date = fields.Datetime(string='Issued Date')
    issued_by = fields.Many2one('res.users', string='Issued by',
                                help='The user who would issue the parts')


class TripPartsHistoryDetails(models.Model):
    """Trip Parts History Details."""

    _name = 'trip.encoded.history'
    _description = 'Trip History'

    def _get_encoded_qty(self):
        res = {}
        for parts_load in self:
            res[parts_load.id] = 0.0
            total__encode_qty = 0.0
            if parts_load.team_id and parts_load.team_id.wo_parts_ids:
                query = "select sum(used_qty) from \
                            workorder_parts_history_details where \
                            product_id=" + str(parts_load.product_id.id) + \
                        " and team_id=" + str(parts_load.team_id.id)
                self._cr.execute(query)
                result = self._cr.fetchone()
                total__encode_qty = result and result[0] or 0.0
                parts_load.write({'encoded_qty': total__encode_qty})
            if total__encode_qty:
                res[parts_load.id] = total__encode_qty
        return res

    def _get_available_qty(self):
        for rec in self:
            available_qty = rec.used_qty - rec.dummy_encoded_qty
            if available_qty < 0:
                raise Warning(_('Quantity Available '
                                'must be greater than zero!'))
            rec.available_qty = available_qty

    product_id = fields.Many2one('product.product', string='Part No',
                                 help='The Part Number')
    part_name = fields.Char(string='Part Name', size=128, translate=True)
    used_qty = fields.Float(string='Used Qty',
                            help='The Quantity that is used in in \
                                    Contact Team Trip')
    encoded_qty = fields.Float(string='Encoded Qty',
                               help='The Quantity that is used in \
                                        in Workorder')
    dummy_encoded_qty = fields.Float(compute="_get_encoded_qty",
                                     string='Dummy Encoded Qty')
    available_qty = fields.Float(compute="_get_available_qty",
                                 string='Qty for Encoding',
                                 help='The Quantity which is available to use')


class TripPartsHistoryDetailsTemp(models.Model):
    """Trip Parts History Details Temp."""

    _name = 'trip.encoded.history.temp'
    _description = 'Trip History Temparery'

    product_id = fields.Many2one('product.product', string='Part No',
                                 help='The Part Number')
    used_qty = fields.Float(string='Used Qty',
                            help='The Quantity that is used in in Workorder')
    work_order_id = fields.Many2one('fleet.vehicle.log.services',
                                    string="Service Order")


class StockPicking(models.Model):
    """Stock Picking."""

    _inherit = 'stock.picking'
    _order = 'id desc'

    work_order_out_id = fields.Many2one('fleet.vehicle.log.services',
                                        string="Work Order ")
    work_order_old_id = fields.Many2one('fleet.vehicle.log.services',
                                        string="Work Order")
    work_order_reopen_id = fields.Many2one('fleet.vehicle.log.services',
                                           string=" Work Order")
    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    received_by_id = fields.Many2one('res.users', string='Received By')

    @api.model
    def create(self, vals):
        """Overridden create method."""
        if vals.get('origin', False) and vals['origin'][0] == ':':
            vals.update({'origin': vals['origin'][1:]})
        if vals.get('origin', False) and vals['origin'][-1] == ':':
            vals.update({'origin': vals['origin'][:-1]})
        return super(StockPicking, self).create(vals)

    def write(self, vals):
        """Overridden write method."""
        if vals.get('origin', False) and vals['origin'][0] == ':':
            vals.update({'origin': vals['origin'][1:]})
        if vals.get('origin', False) and vals['origin'][-1] == ':':
            vals.update({'origin': vals['origin'][:-1]})
        print("write", vals)
        return super(StockPicking, self).write(vals)

    def do_partial_from_migration_script(self):
        """Do partial from migration script method."""
        assert len(self._ids) == 1, 'Partial picking processing \
                                    may only be done one at a time.'
        stock_move = self.env['stock.move']
        uom_obj = self.env['uom.uom']
        partial = self and self[0]
        partial_data = {
            'delivery_date': partial and partial.date or False
        }
        picking_type = ''
        if partial and partial.picking_type_id and \
                partial.picking_type_id.code == 'incoming':
            picking_type = 'in'
        elif partial and partial.picking_type_id and \
                partial.picking_type_id.code == 'outgoing':
            picking_type = 'out'
        elif partial and partial.picking_type_id and \
                partial.picking_type_id.code == 'internal':
            picking_type = 'int'
        for wizard_line in partial.move_lines:
            line_uom = wizard_line.product_uom
            move_id = wizard_line.id

            # Compute the quantity for respective wizard_line in
            # the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(line_uom.id,
                                                   wizard_line.product_qty,
                                                   line_uom.id)

            if line_uom.factor and line_uom.factor != 0:
                if float_compare(qty_in_line_uom, wizard_line.product_qty,
                                 precision_rounding=line_uom.rounding) != 0:
                    raise Warning(_('The unit of measure \
                            rounding does not allow you to ship "%s %s", \
                            only rounding of "%s %s" is accepted by the \
                            Unit of Measure.') % (wizard_line.product_qty,
                                                  line_uom.name,
                                                  line_uom.rounding,
                                                  line_uom.name))
            if move_id:
                # Check rounding Quantity.ex.
                # picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                # partial delivery: 253g
                # => result= refused, as the qty left on picking
                # would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.product_uom
                # Compute the quantity for respective
                # wizard_line in the initial uom
                qty_in_initial_uom = \
                    uom_obj._compute_qty(line_uom.id,
                                         wizard_line.product_qty,
                                         initial_uom.id)
                without_rounding_qty = (wizard_line.product_qty /
                                        line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty,
                                 precision_rounding=initial_uom.rounding) != 0:
                    raise Warning(_('The rounding of the \
                        initial uom does not allow you to ship "%s %s", \
                        as it would let a quantity of "%s %s" to ship and \
                        only rounding of "%s %s" is accepted \
                        by the uom.') % (wizard_line.product_qty,
                                         line_uom.name,
                                         wizard_line.product_qty -
                                         without_rounding_qty,
                                         initial_uom.name,
                                         initial_uom.rounding,
                                         initial_uom.name))
            else:
                seq_obj_name = 'stock.picking.' + picking_type
                move_id = stock_move.create({
                    'name': self.env['ir.sequence'].next_by_code(
                        seq_obj_name),
                    'product_id': wizard_line.product_id and
                                  wizard_line.product_id.id or False,
                    'product_qty': wizard_line.product_qty,
                    'product_uom': wizard_line.product_uom and
                                   wizard_line.product_uom.id or False,
                    'prodlot_id': wizard_line.prodlot_id and
                                  wizard_line.prodlot_id.id or False,
                    'location_id': wizard_line.location_id and
                                   wizard_line.location_id.id or False,
                    'location_dest_id': wizard_line.location_dest_id and
                                        wizard_line.location_dest_id.id or False,
                    'picking_id': partial and partial.id or False
                })
                move_id.action_confirm()
            partial_data['move%s' % (move_id.id)] = {
                'product_id': wizard_line.product_id and
                              wizard_line.product_id.id or False,
                'product_qty': wizard_line.product_qty,
                'product_uom': wizard_line.product_uom and
                               wizard_line.product_uom.id or False,
                'prodlot_id': wizard_line.prodlot_id and
                              wizard_line.prodlot_id.id or False,
            }
            product_currency_id = \
                wizard_line.product_id.company_id.currency_id and \
                wizard_line.product_id.company_id.currency_id.id or False
            picking_currency_id = \
                partial.company_id.currency_id and \
                partial.company_id.currency_id.id or False
            if (picking_type == 'in') and \
                    (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % wizard_line.id].update(
                    product_price=wizard_line.product_id.standard_price,
                    product_currency=product_currency_id or
                                     picking_currency_id or False)
        partial.do_partial(partial_data)
        if partial.purchase_id:
            partial.purchase_id.write({'state': 'done'})
        return True


# class StockMove(models.Model):
#     """Stock Move."""
#
#     _inherit = 'stock.move'
#     _order = 'id desc'
#
#     type = fields.Many2one(related='picking_id.picking_type_id',
#                            string='Shipping Type',
#                            store=True)
#     issued_received_by_id = fields.Many2one('res.users', string='Received By')
#
#     @api.onchange('picking_type_id', 'location_id', 'location_dest_id')
#     def onchange_move_type(self):
#         """On change of move type gives sorce and destination location."""
#         if not self.location_id and not self.location_dest_id:
#             mod_obj = self.env['ir.model.data']
#             location_source_id = 'stock_location_stock'
#             location_dest_id = 'stock_location_stock'
#             if self.picking_type_id and \
#                     self.picking_type_id.code == 'incoming':
#                 location_source_id = 'stock_location_suppliers'
#                 location_dest_id = 'stock_location_stock'
#             elif self.picking_type_id and \
#                     self.picking_type_id.code == 'outgoing':
#                 location_source_id = 'stock_location_stock'
#                 location_dest_id = 'stock_location_customers'
#             source_location = mod_obj.get_object_reference('stock',
#                                                            location_source_id)
#             dest_location = mod_obj.get_object_reference('stock',
#                                                          location_dest_id)
#             self.location_id = source_location and source_location[1] or False
#             self.location_dest_id = dest_location and dest_location[1] or False
#
#     @api.model
#     def _default_location_source(self):
#         location_id = super(StockMove, self)._default_location_source()
#         if self._context.get('stock_warehouse_id', False):
#             warehouse_pool = self.env['stock.warehouse']
#             for rec in warehouse_pool.browse(
#                     [self._context['stock_warehouse_id']]):
#                 if rec.lot_stock_id:
#                     location_id = rec.lot_stock_id.id
#         return location_id
#
#     @api.model
#     def _default_location_destination(self):
#         location_dest_id = super(StockMove, self)._default_location_source()
#         if self._context.get('stock_warehouse_id', False):
#             warehouse_pool = self.env['stock.warehouse']
#             for rec in warehouse_pool.browse(
#                     [self._context['stock_warehouse_id']]):
#                 if rec.wh_output_id_stock_loc_id:
#                     location_dest_id = rec.wh_output_id_stock_loc_id and \
#                                        rec.wh_output_id_stock_loc_id.id or False
#         return location_dest_id


class FleetWorkOrderSearch(models.TransientModel):
    """Fleet Work order search model."""

    _name = 'fleet.work.order.search'
    _description = 'Fleet Work order Search'
    _rec_name = 'state'

    state = fields.Selection([('confirm', 'Open'), ('done', 'Close'),
                              ('draft', 'Draft')], string='Status')
    work_order_id = fields.Many2one('fleet.vehicle.log.services',
                                    string='Service Order')
    fmp_id = fields.Many2one('fleet.vehicle', string='Vehicle ID')

    @api.onchange('fmp_id')
    def _onchange_vehicle_id(self):
        if self.fmp_id:
            return {'domain': {'work_order_id': [
                ('vehicle_id', '=', self.fmp_id.id)
            ]}}
        else:
            return {'domain': {'work_order_id': []}}

    def get_work_order_detail_by_advance_search(self):
        """Method to get work order detail by advance search."""
        domain = []
        order_ids = []
        for order in self:
            if order.work_order_id:
                order_ids.append(order.work_order_id.id)
            if order.work_order_id:
                domain += [('id', 'in', order_ids)]

            return {
                'name': _('Work Order'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'fleet.vehicle.log.services',
                'type': 'ir.actions.act_window',
                # 'nodestroy': True,
                'domain': domain,
                'context': self._context,
                'target': 'current',
            }
        return True


class ResUsers(models.Model):
    """Res Users Model."""

    _inherit = 'res.users'

    usersql_id = fields.Char(string='User ID',
                             help="Take this field for data migration", translate=True)


class IrAttachment(models.Model):
    """Ir Attachment model."""

    _inherit = 'ir.attachment'

    wo_attachment_id = fields.Many2one('fleet.vehicle.log.services')


class ServiceTask(models.Model):
    """Service Task Model."""

    _name = 'service.task'
    _description = 'Maintenance of the Task '

    main_id = fields.Many2one('fleet.vehicle.log.services',
                              string='Maintenance Reference')
    type = fields.Many2one('fleet.service.type', string='Type')
    total_type = fields.Float(string='Cost', readonly=True, default=0.0)
    product_ids = fields.One2many('task.line', 'task_id', string='Product')
    maintenance_info = fields.Text(string='Information', translate=True)


class TaskLine(models.Model):
    """Task Line Model."""

    _name = 'task.line'
    _description = 'Task Line'

    task_id = fields.Many2one('service.task',
                              string='task reference')
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services',
                                       string='Vehicle Work Order')
    product_id = fields.Many2one('product.product', string='Part', domain="[('is_part', '=', True), ('type','!=', 'service')]")
    qty_hand = fields.Float(string='Qty on Hand',
                            help='Quantity on Hand')
    qty = fields.Float(string='Used', default=1.0)
    product_uom = fields.Many2one('uom.uom', string='UOM')
    price_unit = fields.Float(string='Unit Cost')
    total = fields.Float(string='Total Cost')
    date_issued = fields.Datetime(string='Date issued')
    issued_by = fields.Many2one('res.users', string='Issued By',
                                default=lambda self: self._uid)
    is_deliver = fields.Boolean(string="Is Deliver?", store=True)
    is_invoice = fields.Boolean(string="Is invoice?", default=False, store=True)

    def unlink(self):
        for val in self:
            if not val.is_invoice: 
                line = super(TaskLine, self).unlink()
                return line
            elif val.fleet_service_id.state == 'approved':
                line = super(TaskLine, self).unlink()
                return line
            else:
                raise ValidationError(_("You can not delete paid value"))

    @api.onchange('repair_type_id')
    @api.constrains('qty', 'qty_hand')
    def _check_used_qty(self):
        for rec in self:
            if rec.qty <= 0:
                raise Warning(_('You can\'t '
                                'enter used quantity as Zero!'))

    @api.onchange('product_id', 'qty')
    def _onchange_product(self):
        for rec in self:
            if rec.product_id:
                prod = rec.product_id
                if prod.in_active_part:
                    rec.product_id = False
                    raise Warning(_('You can\'t select '
                                    'part which is In-Active!'))
                rec.qty_hand = prod.qty_available or 0.0
                rec.product_uom = prod.uom_id or False
                rec.price_unit = prod.list_price or 0.0
            if rec.qty and rec.price_unit:
                rec.total = rec.qty * rec.price_unit

    @api.model
    def create(self, vals):
        """
        Overridden create method to add the issuer.

        of the part and the time when it was issued.
        """
        # product_obj = self.env['product.product']
        if not vals.get('issued_by', False):
            vals.update({'issued_by': self._uid})
        if not vals.get('date_issued', False):
            vals.update({'date_issued':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        if vals.get('fleet_service_id', False) and \
                vals.get('product_id', False):
            task_line_ids = self.search([
                ('fleet_service_id', '=', vals['fleet_service_id']),
                ('is_invoice', '=', vals['is_invoice']),
                ('product_id', '=', vals['product_id'])
            ])
            if task_line_ids:
                warrnig = 'You can not have duplicate '
                'parts assigned !!!'
                raise Warning(_(warrnig))
        return super(TaskLine, self).create(vals)

    def write(self, vals):
        """
        Overridden write method to add the issuer of the part.

        and the time when it was issued.
        """
        if vals.get('product_id', False) \
                or vals.get('qty', False) \
                or vals.get('product_uom', False) \
                or vals.get('price_unit', False) \
                or vals.get('old_part_return') in (True, False):
            vals.update({'issued_by': self._uid,
                         'date_issued':
                             time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        print("new",vals)
        return super(TaskLine, self).write(vals)

    @api.onchange('date_issued')
    def check_onchange_part_issue_date(self):
        """Onchange method to check the validation for part issues date."""
        context_keys = self._context.keys()
        if 'date_open' in context_keys and self.date_issued:
            date_open = self._context.get('date_open')
            if date_open:
                date_open = datetime.strptime(date_open,
                                              DEFAULT_SERVER_DATE_FORMAT)
                current_date = datetime.now().date()
                #
                if not self.date_issued >= date_open and \
                        not self.date_issued <= current_date:
                    self.date_issued = False
                    raise Warning(_('You can\t enter '
                                    'parts issue either open work order date or in '
                                    'between open work order date and current date!'))
            else:
                self.date_issued = datetime.now().date()

    # def unlink(self):
    #     """Overridden method to add validation before delete the history."""
    #     for part in self:
    #         if part.fleet_service_id.state == 'done':
    #             raise Warning(_("You can't delete part those already used."))
    #         if part.is_deliver:
    #             raise Warning(_("You can't delete part those already used."))
    #     return super(TaskLine, self).unlink()


class RepairType(models.Model):
    """Repair Type."""

    _name = 'repair.type'
    _description = 'Vehicle Repair Type'

    name = fields.Char(string='Repair Type',
                       translate=True)
    product = fields.Many2one('product.product', 'Product', domain="[('is_part', '=', True), ('type','=', 'service')]")
    mechanic = fields.Many2one('res.users', 'Engineer', domain=[('is_mechanic', '=', True)])
    helper = fields.Many2one('res.users', 'Assistance', domain=[('is_mechanic', '=', True)])

    @api.constrains('name')
    def check_repair_type(self):
        for repair in self:
            if self.search_count([
                ('id', '!=', repair.id),
                ('name', 'ilike', repair.name.strip())
            ]):
                raise ValidationError(_('Repair type with this name already exists!'))


class ServiceRepairLine(models.Model):
    """Service Repair Line."""

    _name = 'service.repair.line'
    _description = 'Service Repair Line'

    @api.constrains('date', 'target_date')
    def check_target_completion_date(self):
        """Method to check target completion date."""
        for vehicle in self:
            if vehicle.issue_date and vehicle.target_date:
                if vehicle.target_date < vehicle.issue_date:
                    raise ValidationError('Target Completion Date Should Be '
                                          'Greater Than Issue Date.')

    @api.constrains('target_date', 'date_complete')
    def check_date(self):
        """Method to check etic date."""
        for vehicle in self:
            if vehicle.target_date and vehicle.date_complete:
                if vehicle.target_date > vehicle.date_complete:
                    raise ValidationError('Repairs target completion date should be '
                                          'less than estimated date.')

    service_id = fields.Many2one('fleet.vehicle.log.services',
                                 ondelete='cascade')
    repair_type_id = fields.Many2one('repair.type', string='Repair Type')
    estimated_time = fields.Float(related='repair_type_id.product.estimated_time', readonly=False,
                                  compute='_calcuate_time', string='Estimated time')
    estimated_time2 = fields.Float(store=True, readonly=False, string='Estimated time')
    price = fields.Float('Price', store=True)

    categ_id = fields.Many2one('service.category', string='Category')
    issue_date = fields.Date(string='Issued Date ')
    date_complete = fields.Date(related='service_id.date_complete',
                                string="Complete Date")
    target_date = fields.Date(string='Target Completion')
    complete = fields.Boolean(string='Completed',  default= True,store=True)
    approve = fields.Many2one('res.users', string='Approved by')
    mechanic = fields.Many2one(related='repair_type_id.mechanic', readonly=False, store_true=True)
    helper = fields.Many2one(related='repair_type_id.helper', readonly=False, store_true=True)
    condition = fields.Selection(
        [('harsh', 'Harsh'),
         ('clean', 'clean')],
        string='Condition')
    type = fields.Selection([
        ('inspect', 'Inspect'),
        ('replace', 'Replace'),
        ('repair', 'Repair'),
        ('clean', 'Clean')],
        string='Operations')
    is_preventive = fields.Boolean(default=False , store=True)
    fmp_id = fields.Char(string="Vehicle ID", related='service_id.fmp_id', store="True")
    state = fields.Selection(related='service_id.state', store_true=True)
    is_invoiced = fields.Boolean(default=False, string="test", store=True)
    is_source = fields.Boolean(default=False, string="Out source", store=True)

    # def create(self, vals):
    #     print("create")
    #     for data in vals:
    #         repair_type_id = data['repair_type_id']
    #         services = self.env['repair.type'].search([
    #             ('id', '=', repair_type_id)])
    #         service_lines =  self.env['fleet.vehicle.log.services'].search([
    #         ('id', '=', self.service_id.id)])
    #         if not service_lines.pre_main:
    #             for service_lines in service_lines:
    #                 for line in service_lines.repair_line_ids:
    #                     id = line.repair_type_id.ids
    #                     repair = service_lines.env['repair.type'].search([('id', '=', id)]).product
    #                     product = service_lines.env['product.product'].search([('id', '=', repair.id)])
    #                     line.estimated_time2 = product.estimated_time
    #                     if product.estimated_time:
    #                         payment_per_hour = service_lines.env["res.config.settings"].search([], limit=1,
    #                                                                                   order='id desc').payment_per_hour
    #                         price = payment_per_hour
    #                         line.price = price * product.estimated_time
    #
    #                 payment_per_hour = self.env["res.config.settings"].search([], limit=1,
    #                                                                           order='id desc').payment_per_hour
    #                 price = float(line.estimated_time2) * payment_per_hour
    #                 data['price'] = float(price)
    #     line = super(ServiceRepairLine, self).create(vals)
    #     return line
    def unlink(self):
     for val in self:
       if not val.is_invoiced:
            line = super(ServiceRepairLine, self).unlink()
            return line
       elif val.service_id.state == 'approved':
           line = super(ServiceRepairLine, self).unlink()
           return line
       else:
           raise ValidationError(_("You can not delete paid value"))

    @api.onchange('repair_type_id')
    def get_repair_line(self):
        for repair_type in self:
          if repair_type.repair_type_id:
            id = repair_type.repair_type_id.id
            repair = repair_type.env['repair.type'].search([('id', '=', id)]).product
            product = repair_type.env['product.product'].search([('id', '=', repair.id)])
            repair_type.estimated_time2 = product.estimated_time
            if product.estimated_time:
                if self.vehicle_id.vechical_type_id.price > 0:
                    payment_per_hour = self.env["res.config.settings"].search([], limit=1,
                                                                              order='id desc').payment_per_hour
                else:
                    payment_per_hour = self.vehicle_id.vechical_type_id.price
                price = payment_per_hour
                repair_type.price = price * product.estimated_time

    @api.depends('repair_type_id')
    def _calcuate_time(self):
        for line in self.repair_type_id:
           id = line.repair_type_id.id
           repair = self.env['repair.type'].search([('id', '=',id)]).ids
           product = self.env['product.template'].search([('id', '=',repair)])
           print("product.stimated_time",product.stimated_time)

    def write(self, vals):
        """Method Write."""
        print("write")
        amount = 0.0

        line = super(ServiceRepairLine, self).write(vals)

        service_lines = self.env['service.repair.line'].search([
            ('service_id', '=', self.service_id.id)])
        for service_line in service_lines:
             amount += service_line.price
        services = self.env['fleet.vehicle.log.services'].search([
            ('id', '=', self.service_id.id)])
        for service in services:
            service.write({'amount2': amount})

        return line

    # @api.onchange('complete')
    # def onchange_complete(self):
    #     if self.state != 'confirm' and :
    #         raise ValidationError(_("You can not complete because the service is not open"))



class FleetServiceType(models.Model):
    """Fleet Service Type."""

    _inherit = 'fleet.service.type'

    category = fields.Selection(selection_add=[
        ('contract', 'Contract'),
        ('service', 'Service'),
        ('both', 'Both')],
        required=False,
        string='Category',
        help="Choose whether the service refer to contracts, "
             "vehicle services or both")
    repair_type_ids = fields.Many2many('repair.type',
                                       'fleet_service_repair_type_rel',
                                       'service_type_id', 'reapir_type_id',
                                       string='Repair Type')
