
from odoo import api, fields, models

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

class StockMove(models.Model):
    _inherit = "stock.move"


    def action_assign_serial_show_details(self):
        """ On `self.move_line_ids`, assign `lot_name` according to
        `self.next_serial` before returning `self.action_show_details`.
        """
        search  = self.env['product.product'].search([('id','=',self.product_id.id)])
        domain = [('product_id','=',self.product_id.id)]
        search_cat  = self.env['product.category'].search([('id','=',search.categ_id.id)], limit=1)
        search_result = self.search(domain, order='id DESC')
        lot_search  = self.env['stock.production.lot'].search(domain, order='id DESC')
        last_id = lot_search[0] if lot_search else None
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
                initial_number = int(initial_number)
                get_next_serial = self.inspection_success_qty
                lot_names = []
                lot_new =[]
                search_lot = self.env['ir.sequence'].search([('code','=','stock.move')])
                if search_cat.cat_code is False:
                    lot_prefix = search_lot.prefix+"/"
                else:
                    lot_prefix = search_lot.prefix + search_cat.cat_code + "/"
                if search_lot.suffix == False:
                    lot_suffix = ' '
                else:
                    lot_suffix = search_lot.suffix
                for i in range(1, int(get_next_serial)+2):
                    lot_names.append('%s%s%s' % (
                        prefix,
                        str(initial_number + i).zfill(padding),
                        suffix
                    ))
                    lot_new.append('%s%s%s' % (
                        lot_prefix, 
                        str(initial_number+i).zfill(padding),
                         lot_suffix
                    ))
                _logger.info("OOOOOOOOOOOOOOOOOO %s",lot_new)

            
                if int(get_next_serial) > 0:
                    _logger.info("*******lot_names**** %s",lot_names)
                    _logger.info("*******lot_names**** %s",lot_names[1])        
                    self.next_serial = lot_names[0]
                    self.next_serial_count = int(get_next_serial)

                else:
                    for i in range(1, 3):
                        lot_names.append('%s%s%s' % (
                        prefix,
                        str(initial_number + i).zfill(padding),
                        suffix
                        ))
                    self.next_serial = lot_names[1]


                if not self.next_serial:
                    raise UserError(_("You need to set a Serial Number before generating more."))
                self._generate_serial_numbers()
                return self.action_show_details()
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
                search_lot = self.env['ir.sequence'].search([('code','=','stock.move')])
                lot_names = []
                lot_new =[]
                search_lot = self.env['ir.sequence'].search([('code','=','stock.move')])
                if search_cat.cat_code is False:
                    lot_prefix = search_lot.prefix+"/"
                else:
                    lot_prefix = search_lot.prefix + search_cat.cat_code + "/"
                if search_lot.suffix == False:
                    lot_suffix = ' '
                else:
                    lot_suffix = search_lot.suffix
                for i in range(1, int(get_next_serial)+2):
                    lot_names.append('%s%s%s' % (
                        prefix,
                        str(initial_number + i).zfill(padding),
                        suffix
                    ))
                    lot_new.append('%s%s%s' % (
                        lot_prefix, 
                        str(initial_number+i).zfill(padding),
                         lot_suffix
                    ))
                self.ensure_one()
            
                if int(get_next_serial) > 0:
                    _logger.info("*******lot_names**** %s",lot_names)
                    _logger.info("*******lot_names**** %s",lot_names[1])        
                    self.next_serial = lot_names[0]
                    self.next_serial_count = int(get_next_serial)

                else:
                    for i in range(1, 3):
                        lot_names.append('%s%s%s' % (
                        prefix,
                        str(initial_number + i).zfill(padding),
                        suffix
                        ))
                    self.next_serial = lot_names[1]
                if not self.next_serial:
                    raise UserError(_("You need to set a Serial Number before generating more."))
                self._generate_serial_numbers()
                return self.action_show_details()
        else:
            _logger.info("############# Not Storable###############")

            pass

class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_picking = fields.Boolean(default=False)


    @api.onchange('picking_type_id')
    def _onchange_picking_type(self):
        if self.picking_type_id.code == 'outgoing' or self.picking_type_id.code == 'internal':
            self.is_picking = True


    def action_auto_assign(self):
        """ On `self.move_line_ids`, assign `lot_name` according to
        `self.next_serial` before returning `self.action_show_details`.
        """
        _logger.info("#############action_auto_assign##############")
        picking_id = self.id
        for loop in self.move_ids_without_package:
            _logger.info("QQQQQQQQQQQ %s", loop.quantity_done)
            if loop.quantity_done > 0:
                pass
            else:
                loop.action_assign_serial_show_details()
                # loop.quantity_done = loop.inspection_success_qty
                check_PO = self.env['stock.move.line'].search([('move_id','=',loop.id)])
                for l in check_PO:
                    if not l.lot_name:
                        pass
                    else:
                        lot_list = self.env['stock.production.lot'].search([('name','=',l.lot_name)])
                    
        
        