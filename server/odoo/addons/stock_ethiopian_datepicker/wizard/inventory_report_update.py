# See LICENSE file for full copyright and licensing details.
"""Update History Wizard."""

from datetime import datetime
import logging
from datetime import date
from datetime import datetime, timedelta,date
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os
from odoo.osv import expression
from odoo.exceptions import UserError, Warning, ValidationError
import re
import base64
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
from ethiopian_date import EthiopianDateConverter
pick1 = []
pick2 = []
pick3 = []
pick4 = []



class StockQuantityUpdate(models.TransientModel):
    """Update Engine Info."""

    _inherit = 'stock.quantity.history'


# To use code for a single date in a wizard, 

# you should copy the code from line 39 to the end of the date_convert_and_set function, 



    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')


    
    @api.model
    def initial_date(self, data):
        date = datetime.now()
        data = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
        return data

    @api.model
    def date_convert_and_set(self,picked_date):
        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date,time = str(datetime.now()).split(" ")
        dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
        # date = str(date_et) + " " + str(f"{time}")
        date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
        date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
        data = {
            'day':   picked_date['day'],
            'month': picked_date['month'],
            'year': picked_date['year'],
            'pick': picked_date['pick']
        }
        if picked_date['pick'] == 1:
            pick1.append(data)
       
    def open_at_date(self):
        _logger.info("***************pick1 %s",pick1)
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        ethiopian_from = Edate1
                        pick1.clear()
                    if type(Edate1) ==   date:
                        ethiopian_from = Edate1

                        pick1.clear()

        tree_view_id = self.env.ref('stock.view_stock_product_tree').id
        form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
        domain = [('type', '=', 'product')]
        product_id = self.env.context.get('product_id', False)
        product_tmpl_id = self.env.context.get('product_tmpl_id', False)
        if product_id:
            domain = expression.AND([domain, [('id', '=', product_id)]])
        elif product_tmpl_id:
            domain = expression.AND([domain, [('product_tmpl_id', '=', product_tmpl_id)]])
        # We pass `to_date` in the context so that `qty_available` will be computed across
        # moves until date.
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
            'view_mode': 'tree,form',
            'name': _('Products'),
            'res_model': 'product.product',
            'domain': domain,
            'context': dict(self.env.context, to_date=self.inventory_datetime),
        }
        return action
