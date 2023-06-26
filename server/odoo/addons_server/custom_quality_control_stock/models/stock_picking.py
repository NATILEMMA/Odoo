
from odoo import api, fields, models

from odoo.addons.custom_quality_control.models.qc_trigger_line import _filter_trigger_lines
import logging
from odoo.exceptions import UserError, Warning, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from ast import literal_eval
from datetime import date
from itertools import groupby
from operator import attrgetter, itemgetter
from collections import defaultdict
import time, logging
_logger = logging.getLogger(__name__)
from re import findall as regex_findall, split as regex_split
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo import api, fields, models, SUPERUSER_ID, _,exceptions
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES

_logger = logging.getLogger(__name__)


class ProductLot(models.Model):
    _inherit = "stock.production.lot"  

    purchase_ref = fields.Many2one('purchase.order', string="Purchase Reference")



class StockAssignSerialNumbers(models.TransientModel):
    _inherit = 'stock.assign.serial'

    inspection_success_qty = fields.Float()
    inspection_failed_qty = fields.Float()
    # next_serial_number = fields.Char('First SN', default=_default_next_serial_number,required=True)
    # next_serial_count = fields.Integer('Number of SN',
    #     default=_default_next_serial_count_1, required=True)

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    purchase_ref = fields.Many2one('purchase.order', string="Purchase Reference")

class StockMove(models.Model):
    _inherit = "stock.move"

    inspection_success_qty = fields.Float()
    inspection_failed_qty = fields.Float()
    is_insepction_needed = fields.Boolean(default=True)


    
    # def action_assign_serial_show_details(self):
    #     res = super().action_assign_serial_show_details()
    #     _logger.info("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
    def _generate_serial_numbers(self, next_serial_count=False):
        """ This method will generate `lot_name` from a string (field
        `next_serial`) and create a move line for each generated `lot_name`.
        """
        self.ensure_one()

        if not next_serial_count:
            next_serial_count = self.next_serial_count
        # We look if the serial number contains at least one digit.
        caught_initial_number = regex_findall("\d+", self.next_serial)
        if not caught_initial_number:
            raise UserError(_('The serial number must contain at least one digit.'))
        # We base the serie on the last number find in the base serial number.
        initial_number = caught_initial_number[-1]
        padding = len(initial_number)
        # We split the serial number to get the prefix and suffix.
        splitted = regex_split(initial_number, self.next_serial)
        # initial_number could appear several times in the SN, e.g. BAV023B00001S00001
        prefix = initial_number.join(splitted[:-1])
        suffix = splitted[-1]
        initial_number = int(initial_number)

        lot_names = []
        purchasOrder = []
        _logger.info("sssssssssssssssssssss pikcing_id",self.picking_id.id)
        search = self.env['stock.picking'].search([('id','=',self.picking_id.id)])
        for i in range(0, next_serial_count):
            lot_names.append('%s%s%s' % (
                prefix,
                str(initial_number + i).zfill(padding),
                suffix
            ))
            purchasOrder.append(search.id)

        _logger.info("******purchasOrder %s",purchasOrder)
        move_lines_commands = self._generate_serial_move_line_commands(lot_names)
        _logger.info("bbbbbbbbbbbbbbbbxxxxxxxxxxxxxxxxxxxxx %s",move_lines_commands)
        _logger.info("Ppppppppppppself.picking_id %s",self.picking_id)
        po = self.env['purchase.order'].search([('name','=', self.origin)])
        _logger.info(".picking_id %s",po.name)

        purchaseOrder = []
        for i in lot_names:
            purchaseOrder.append(po.id)
        self.write({'move_line_ids': move_lines_commands})
        # self.write({'purchase_ref': purchaseOrder})
        
        return True
    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None):
        """Return a list of commands to update the move lines (write on
        existing ones or create new ones).
        Called when user want to create and assign multiple serial numbers in
        one time (using the button/wizard or copy-paste a list in the field).

        :param lot_names: A list containing all serial number to assign.
        :type lot_names: list
        :param origin_move_line: A move line to duplicate the value from, default to None
        :type origin_move_line: record of :class:`stock.move.line`
        :return: A list of commands to create/update :class:`stock.move.line`
        :rtype: list
        """
        _logger.info("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP:%s",lot_names)
        # _logger.info("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP:%s",purchasOrder)


        self.ensure_one()

        # Select the right move lines depending of the picking type configuration.
        move_lines = self.env['stock.move.line']
        if self.picking_type_id.show_reserved:
            move_lines = self.move_line_ids.filtered(lambda ml: not ml.lot_id and not ml.lot_name and not ml.purchase_ref)
        else:
            move_lines = self.move_line_nosuggest_ids.filtered(lambda ml: not ml.lot_id and not ml.lot_name and not ml.purchase_ref)

        if origin_move_line:
            location_dest = origin_move_line.location_dest_id
        else:
            location_dest = self.location_dest_id._get_putaway_strategy(self.product_id)
        poO = self.env['purchase.order'].search([('name','=', self.origin)])
        
        move_line_vals = {
            'picking_id': self.picking_id.id,
            'location_dest_id': location_dest.id or self.location_dest_id.id,
            'location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,
            'qty_done': 1,
           
        }
        if origin_move_line:
            # `owner_id` and `package_id` are taken only in the case we create
            # new move lines from an existing move line. Also, updates the
            # `qty_done` because it could be usefull for products tracked by lot.
            move_line_vals.update({
                'owner_id': origin_move_line.owner_id.id,
                'package_id': origin_move_line.package_id.id,
                'qty_done': origin_move_line.qty_done or 1,
            })

        move_lines_commands = []
        move_lines_commands_1 = []

        for lot_name in lot_names:
            _logger.info("Ppppppppppppself.picking_id %s",self.picking_id)
            po = self.env['purchase.order'].search([('name','=', self.origin)])
            _logger.info(".picking_id %s",po.name)

            purchaseOrder = []
            for i in lot_name:
                purchaseOrder.append(po.id)

            # _logger.info("GGGGGGGGGG.picking_id %s",purchaseOrder)
            
            # We write the lot name on an existing move line (if we have still one)...
            if move_lines:
               
                move_lines_commands.append((1, move_lines[0].id, {
                    'lot_name': lot_name,
                    'qty_done': 1,
                    'purchase_ref': po.id
                }))
                move_lines = move_lines[1:]
            # ... or create a new move line with the serial name.
            else:
                
                move_lines = move_lines[1:]
            
                move_line_cmd = dict(move_line_vals, lot_name=lot_name,purchase_ref= po.id)
                # move_line_cmd_1 = dict(move_line_vals,purchase_ref= purchasOrder)

                move_lines_commands.append((0, 0, move_line_cmd))
                # move_lines_commands_1.append((0, 0, move_line_cmd_1))

        return move_lines_commands




    def action_show_details(self,next_serial_count=False):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()
      
        # If "show suggestions" is not checked on the picking type, we have to filter out the
        # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
        # different views to display one field or another so that the webclient doesn't have to
        # fetch both.
        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('stock.view_stock_move_operations')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        picking_type_id = self.picking_type_id or self.picking_id.picking_type_id

        search  = self.env['product.product'].search([('id','=',self.product_id.id)])
        _logger.info("search:%s",search)
        _logger.info("search:%s",search)
        domain = [('product_id','=',self.product_id.id)]
        search_result = self.search(domain, order='id DESC')
        
        lot_search  = self.env['stock.production.lot'].search(domain, order='id DESC')
        _logger.info("lot_search:%s",lot_search)
        last_id = lot_search[0] if lot_search else None
        _logger.info("last_id:%s",last_id)

        if search.type == 'product':
            if not last_id:
                lname = search.name
                lname = lname.upper()
                _logger.info("*****lname****** %s, %s",lname[0], lname[-1])
                lname = lname[0]+lname[-1]+'000'
                caught_initial_number = regex_findall("\d+", lname)
                _logger.info("*********** %s",caught_initial_number)
                # We base the serie on the last number find in the base serial number.
                initial_number = caught_initial_number[-1]
                padding = len(initial_number)
                _logger.info("******initial_number***** %s",initial_number)

                # We split the serial number to get the prefix and suffix.
                splitted = regex_split(initial_number, lname)
                _logger.info("*********** %s",splitted)

                # initial_number could appear several times in the SN, e.g. BAV023B00001S00001
                prefix = initial_number.join(splitted[:-1])
                suffix = splitted[-1]
                _logger.info("*******prefix**** %s",prefix)
                _logger.info("*******suffix**** %s",suffix)
                initial_number = int(initial_number)
                get_next_serial = self.inspection_success_qty
                lot_names = []
                for i in range(1, int(get_next_serial)+2):
                    lot_names.append('%s%s%s' % (
                        prefix,
                        str(initial_number + i).zfill(padding),
                        suffix
                    ))
                if int(get_next_serial) > 0:
                    _logger.info("*******lot_names**** %s",lot_names)
                    _logger.info("*******lot_names**** %s",lot_names[1])        
                    self.next_serial = lot_names[0]
                    self.next_serial_count = int(get_next_serial)


                    return {
                        'name': _('Detailed Operations'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'stock.move',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': self.id,
                        'context': dict(
                            self.env.context,
                            show_owner=self.picking_type_id.code != 'incoming',
                            show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                            show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                            show_source_location=self.picking_type_id.code != 'incoming',
                            show_destination_location=self.picking_type_id.code != 'outgoing',
                            show_package=not self.location_id.usage == 'supplier',
                            show_reserved_quantity=self.state != 'done' and not self.picking_id.immediate_transfer and self.picking_type_id.code != 'incoming'
                        ),
                    }
                else:
                    _logger.info("############ is_insepction_needed ############ %s",self.is_insepction_needed)
                
                
                    for i in range(1, 3):
                        lot_names.append('%s%s%s' % (
                        prefix,
                        str(initial_number + i).zfill(padding),
                        suffix
                        ))
                    self.next_serial = lot_names[1]
                    
                    if self.is_insepction_needed is False:
                        return {
                        'name': _('Detailed Operations'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'stock.move',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': self.id,
                        'context': dict(
                            self.env.context,
                            show_owner=self.picking_type_id.code != 'incoming',
                            show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                            show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                            show_source_location=self.picking_type_id.code != 'incoming',
                            show_destination_location=self.picking_type_id.code != 'outgoing',
                            show_package=not self.location_id.usage == 'supplier',
                            show_reserved_quantity=self.state != 'done' and not self.picking_id.immediate_transfer and self.picking_type_id.code != 'incoming'
                        ),
                    }
                    else:
                        raise exceptions.UserError(
                                    _(
                                        "To assign a serial number, an inspection result is Inspection success and failed quantity required...! \n\n To Force assign uncheck the Inspection Required box."
                                        
                                    )
                                )
            else:
                caught_initial_number = regex_findall("\d+", last_id.name)
                _logger.info("*********** %s",caught_initial_number)
                # We base the serie on the last number find in the base serial number.
                initial_number = caught_initial_number[-1]
                padding = len(initial_number)
                _logger.info("******initial_number***** %s",initial_number)

                # We split the serial number to get the prefix and suffix.
                splitted = regex_split(initial_number, last_id.name)
                _logger.info("*********** %s",splitted)

                # initial_number could appear several times in the SN, e.g. BAV023B00001S00001
                prefix = initial_number.join(splitted[:-1])
                suffix = splitted[-1]
                _logger.info("*******prefix**** %s",prefix)
                _logger.info("*******suffix**** %s",suffix)
                initial_number = int(initial_number)
                get_next_serial = self.inspection_success_qty
                lot_names = []
                for i in range(1, int(get_next_serial)+2):
                    lot_names.append('%s%s%s' % (
                        prefix,
                        str(initial_number + i).zfill(padding),
                        suffix
                    ))
                if int(get_next_serial) > 0:
                    _logger.info("*******lot_names**** %s",lot_names)
                    _logger.info("*******lot_names**** %s",lot_names[1])        
                    self.next_serial = lot_names[0]
                    self.next_serial_count = int(get_next_serial)


                    return {
                        'name': _('Detailed Operations'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'stock.move',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': self.id,
                        'context': dict(
                            self.env.context,
                            show_owner=self.picking_type_id.code != 'incoming',
                            show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                            show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                            show_source_location=self.picking_type_id.code != 'incoming',
                            show_destination_location=self.picking_type_id.code != 'outgoing',
                            show_package=not self.location_id.usage == 'supplier',
                            show_reserved_quantity=self.state != 'done' and not self.picking_id.immediate_transfer and self.picking_type_id.code != 'incoming'
                        ),
                    }
                else:
                    _logger.info("############ is_insepction_needed ############ %s",self.is_insepction_needed)
                
                
                    for i in range(1, 3):
                        lot_names.append('%s%s%s' % (
                        prefix,
                        str(initial_number + i).zfill(padding),
                        suffix
                        ))
                    self.next_serial = lot_names[1]
                    
                    if self.is_insepction_needed is False:
                        return {
                        'name': _('Detailed Operations'),
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'stock.move',
                        'views': [(view.id, 'form')],
                        'view_id': view.id,
                        'target': 'new',
                        'res_id': self.id,
                        'context': dict(
                            self.env.context,
                            show_owner=self.picking_type_id.code != 'incoming',
                            show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),  # able to create lots, whatever the value of ` use_create_lots`.
                            show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                            show_source_location=self.picking_type_id.code != 'incoming',
                            show_destination_location=self.picking_type_id.code != 'outgoing',
                            show_package=not self.location_id.usage == 'supplier',
                            show_reserved_quantity=self.state != 'done' and not self.picking_id.immediate_transfer and self.picking_type_id.code != 'incoming'
                        ),
                    }
                    else:
                        raise exceptions.UserError(
                                    _(
                                        "To assign a serial number, an inspection result is Inspection success and failed quantity required...! \n\n To Force assign uncheck the Inspection Required box."
                                        
                                    )
                                )
            
        else:
            pass


class StockPicking(models.Model):
    _inherit = "stock.picking"

    qc_inspections_ids = fields.One2many(
        comodel_name="qc.inspection",
        inverse_name="picking_id",
        copy=False,
        string="Inspections",
        help="Inspections related to this picking.",
    )
    created_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Created inspections"
    )
    done_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Done inspections"
    )
    passed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections OK"
    )
    failed_inspections = fields.Integer(
        compute="_compute_count_inspections", string="Inspections failed"
    )
    is_assigned = fields.Boolean(default=False)
    is_insepction_needed = fields.Boolean(default=True)
 

    @api.onchange('is_insepction_needed')
    def _compute_is_insepction_needed(self):
        for l in self.move_ids_without_package:
            stock_move = self.env['stock.move'].search([('id','in',l.ids)])
            if self.is_insepction_needed == True:
                stock_move.is_insepction_needed = True
            else:
                stock_move.is_insepction_needed = False


    @api.depends("qc_inspections_ids", "qc_inspections_ids.state")
    def _compute_count_inspections(self):
        data = self.env["qc.inspection"].read_group(
            [("id", "in", self.mapped("qc_inspections_ids").ids)],
            ["picking_id", "state"],
            ["picking_id", "state"],
            lazy=False,
        )
        picking_data = {}
        for d in data:
            picking_data.setdefault(d["picking_id"][0], {}).setdefault(d["state"], 0)
            picking_data[d["picking_id"][0]][d["state"]] += d["__count"]
        for picking in self:
            count_data = picking_data.get(picking.id, {})
            picking.created_inspections = sum(count_data.values())
            picking.passed_inspections = count_data.get("success", 0)
            picking.failed_inspections = count_data.get("failed", 0)
            picking.done_inspections = (
                picking.passed_inspections + picking.failed_inspections
            )

    def action_done(self):
        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        _logger.info("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        self._check_company()

        todo_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            if pick.owner_id:
                pick.move_lines.write({'restrict_partner_id': pick.owner_id.id})
                pick.move_line_ids.write({'owner_id': pick.owner_id.id})

            # # Explode manually added packages
            # for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
            #     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
            #         self.move_line_ids.create({'product_id': quant.product_id.id,
            #                                    'package_id': quant.package_id.id,
            #                                    'result_package_id': ops.result_package_id,
            #                                    'lot_id': quant.lot_id.id,
            #                                    'owner_id': quant.owner_id.id,
            #                                    'product_uom_id': quant.product_id.uom_id.id,
            #                                    'product_qty': quant.qty,
            #                                    'qty_done': quant.qty,
            #                                    'location_id': quant.location_id.id, # Could be ops too
            #                                    'location_dest_id': ops.location_dest_id.id,
            #                                    'picking_id': pick.id
            #                                    }) # Might change first element
            # # Link existing moves or add moves when no one is related
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create(self._prepare_stock_move_vals(ops, pick))
                    ops.move_id = new_move.id
                    new_move = new_move._action_confirm()
                    todo_moves |= new_move
                    #'qty_done': ops.qty_done})


        todo_moves._action_done(cancel_backorder=self.env.context.get('cancel_backorder'))
        self.write({'date_done': fields.Datetime.now()})
        self._send_confirmation_email()
        purchase_order = self.env['purchase.order'].search([('name','=',self.origin)], limit=1)
        for loop in self.move_ids_without_package:
            check_PO = self.env['stock.move.line'].search([('move_id','=',loop.id)])
            for l in check_PO:
                if not l.lot_name:
                    pass
                else:
                    lot_list = self.env['stock.production.lot'].search([('name','=',l.lot_name)])
                    _logger.info("llllllllllllllll %s",lot_list)
                    lot_list.write({'purchase_ref': purchase_order})
        
        return True
    def button_validate(self):
        if self.is_insepction_needed is True:

            if self.is_assigned is False:  
                raise exceptions.UserError(
                        _(
                            "Before validating, \n"
                            
                            "assign it to inspection, and then validating based on the outcome of quality control! , \n\nOr uncheck Inspection needed box"  #\n\n Or Or, uncheck Inspection needed box")
                        )
                    )
                
            elif not self.done_inspections:
                raise ValidationError("Done Inspection Zero, you must complete the inspection.")  #\n\n Or Or, uncheck Inspection needed box")
            elif  self.done_inspections != self.created_inspections:
                # raise ValidationError("You must complete the inspection...! before validate\n")  #\n\n Or Or, uncheck Inspection needed box")
                raise exceptions.UserError(
                        _(
                            "You must complete the inspection...! before validate\n"
                            
                            " There are still "+str(-(int(self.done_inspections)-( self.created_inspections))) + " inspections left to complete the total inspection."
                        )
                    )
            else:
                return super().button_validate()
        else:

            
            return super().button_validate()

    
    def action_inspection(self):
        res = super().action_done()

        for line in self.move_ids_without_package:
            _logger.info("line:%s",line.product_id)
            _logger.info("line:%s",line.product_id.name)
            search  = self.env['product.product'].search([('id','=',line.product_id.id)])
            _logger.info("search:%s",search)
            _logger.info("searchYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY:%s",search.qc_triggers)
            _logger.info("searchYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY:%s",len(search.qc_triggers))
            if len(search.qc_triggers) <= 0:

                raise exceptions.UserError(
                        _(
                            "Before Assign to Inspection, \n"
                            
                            "Add inspection(Quality control) questions to product"  #\n\n Or Or, uncheck Inspection needed box")
                        )
                    )
        # raise ValidationError("Before validate, \nAssign to inspection and Validate based on the quality control result!")  #\n\n Or Or, uncheck Inspection needed box")

        inspection_model = self.env["qc.inspection"]
        _logger.info("##############")
        _logger.info("##############:%s",self.picking_type_id.id)

        qc_trigger = self.env["qc.trigger"].search(
            [("picking_type_id", "=", self.picking_type_id.id)]
        )
        _logger.info("########qc_trigger######:%s",qc_trigger)
        if self.created_inspections > 0:
            _logger.info("##########   no #############")
            pass
        else:
            for operation in self.move_lines:
                trigger_lines = set()
                for model in [
                    "qc.trigger.product_category_line",
                    "qc.trigger.product_template_line",
                    "qc.trigger.product_line",
                ]:
                    _logger.info("********model %s:",model)
                    partner = self.partner_id if qc_trigger.partner_selectable else False
                    trigger_lines = trigger_lines.union(
                        self.env[model].get_trigger_line_for_product(
                            qc_trigger, operation.product_id, partner=partner
                        )
                    )
                for trigger_line in _filter_trigger_lines(trigger_lines):
                    inspection_model._make_inspection(operation, trigger_line)
                self.is_assigned = True
            return res

    # def action_done(self):
    #     res = super().action_done()
    #     inspection_model = self.env["qc.inspection"]
    #     _logger.info("##############")
    #     _logger.info("##############:%s",self.picking_type_id.id)

    #     qc_trigger = self.env["qc.trigger"].search(
    #         [("picking_type_id", "=", self.picking_type_id.id)]
    #     )
    #     _logger.info("########qc_trigger######:%s",qc_trigger)

    #     for operation in self.move_lines:
    #         trigger_lines = set()
    #         for model in [
    #             "qc.trigger.product_category_line",
    #             "qc.trigger.product_template_line",
    #             "qc.trigger.product_line",
    #         ]:
    #             _logger.info("********model %s:",model)
    #             partner = self.partner_id if qc_trigger.partner_selectable else False
    #             trigger_lines = trigger_lines.union(
    #                 self.env[model].get_trigger_line_for_product(
    #                     qc_trigger, operation.product_id, partner=partner
    #                 )
    #             )
    #         for trigger_line in _filter_trigger_lines(trigger_lines):
    #             inspection_model._make_inspection(operation, trigger_line)
    #     return res


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def _process(self, cancel_backorder=False):
        _logger.info("creating back order....... cancel_backorder.........  %s",self.id)
        for confirmation in self:
            if cancel_backorder:
                for pick_id in confirmation.pick_ids:
                    moves_to_log = {}
                    for move in pick_id.move_lines:
                        if float_compare(move.product_uom_qty,
                                         move.quantity_done,
                                         precision_rounding=move.product_uom.rounding) > 0:
                            moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
                    pick_id._log_less_quantities_than_expected(moves_to_log)
            confirmation.pick_ids.with_context(cancel_backorder=cancel_backorder).action_done()

    def process(self):
        _logger.info("process creating back order................")

        self._process()
