import logging
from datetime import date
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os
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


class PurchaseApprovalLimit(models.Model):
    _inherit = "purchase.approval.limit"

    @api.model
    def create(self, vals):
        if vals['max_amount'] < 0:
            vals['max_amount'] = abs(vals['max_amount'])
        if vals['max_amount_2'] < 0:
            vals['max_amount_2'] = abs(vals['max_amount_2'])

        return super(PurchaseApprovalLimit, self).create(vals)

    def write(self, vals):
        try:
            if vals['max_amount'] < 0:
                vals['max_amount'] = abs(vals['max_amount'])
        except:
            pass
        try:
            if vals['max_amount_2'] < 0:
                vals['max_amount_2'] = abs(vals['max_amount_2'])
        except:
            pass

        return super(PurchaseApprovalLimit, self).write(vals)


class TenderLimit(models.Model):
    _inherit = "tender.limit"

    @api.model
    def create(self, vals):
        if vals['max_amount'] < 0:
            vals['max_amount'] = abs(vals['max_amount'])
        if vals['max_amount_2'] < 0:
            vals['max_amount_2'] = abs(vals['max_amount_2'])

        return super(TenderLimit, self).create(vals)

    def write(self, vals):
        try:
            if vals['max_amount'] < 0:
                vals['max_amount'] = abs(vals['max_amount'])
        except:
            pass
        try:
            if vals['max_amount_2'] < 0:
                vals['max_amount_2'] = abs(vals['max_amount_2'])
        except:
            pass

            return super(TenderLimit, self).write(vals)


class SprogroupPurchaseRequestLine(models.Model):
    _inherit = "sprogroup.purchase.request.line"

    @api.model
    def create(self, vals):
        if vals['product_qty'] < 0:
            vals['product_qty'] = abs(vals['product_qty'])
        if vals['estimated_price'] < 0:
            vals['estimated_price'] = abs(vals['estimated_price'])

        return super(SprogroupPurchaseRequestLine, self).create(vals)

    def write(self, vals):
        try:
            if vals['product_qty'] < 0:
                vals['product_qty'] = abs(vals['product_qty'])
        except:
            pass
        try:
            if vals['estimated_price'] < 0:
                vals['estimated_price'] = abs(vals['estimated_price'])
        except:
            pass

        return super(SprogroupPurchaseRequestLine, self).write(vals)


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    @api.model
    def create(self, vals):
        if vals['product_qty'] < 0:
            vals['product_qty'] = abs(vals['product_qty'])
        if vals['price_unit'] < 0:
            vals['price_unit'] = abs(vals['price_unit'])

        return super(PurchaseRequisitionLine, self).create(vals)

    def write(self, vals):
        try:
            if vals['product_qty'] < 0:
                vals['product_qty'] = abs(vals['product_qty'])
        except:
            pass
        try:
            if vals['price_unit'] < 0:
                vals['price_unit'] = abs(vals['price_unit'])
        except:
            pass

        return super(PurchaseRequisitionLine, self).write(vals)


class VendorDocument(models.Model):
    _inherit = "vendor.document"

    @api.model
    def create(self, vals):
        if vals['value'] < 0:
            vals['value'] = abs(vals['value'])

        return super(VendorDocument, self).create(vals)

    def write(self, vals):
        try:
            if vals['value'] < 0:
                vals['value'] = abs(vals['value'])
        except:
            pass

        return super(VendorDocument, self).write(vals)


class ProductDocument(models.Model):
    _inherit = "product.document"

    @api.model
    def create(self, vals):
        if vals['value'] < 0:
            vals['value'] = abs(vals['value'])

        return super(ProductDocument, self).create(vals)

    def write(self, vals):
        try:
            if vals['value'] < 0:
                vals['value'] = abs(vals['value'])
        except:
            pass

        return super(ProductDocument, self).write(vals)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def create(self, vals):
        if vals['product_qty'] < 0:
            vals['product_qty'] = abs(vals['product_qty'])

        return super(PurchaseOrderLine, self).create(vals)

    def write(self, vals):
        try:
            if vals['price_unit'] < 0:
                vals['price_unit'] = abs(vals['price_unit'])
        except:
            pass

        return super(PurchaseOrderLine, self).write(vals)


