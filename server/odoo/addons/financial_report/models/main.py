from collections import defaultdict
from distutils.log import error
from itertools import groupby
from re import search

from odoo import api, fields, models,  SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError,Warning
from odoo.tools import float_is_zero, OrderedSet
from datetime import timedelta
from datetime import datetime , time
# from multiprocessing import Process
import logging
_logger = logging.getLogger(__name__)

class Report_update(models.TransientModel):
    _name = "financial.report"
    _inherit = "financial.report"

    fiscal_year=fields.Many2one('fiscal.year',"Fiscal Year",default=lambda self:self._default_fiscal_year())
    period= fields.Many2one('reconciliation.time.fream',"Period",default=lambda self:self._default_period())
    date_from = fields.Date(string='Start Date',default=lambda self:self._default_start_date())
    date_to = fields.Date(string='End Date',default=lambda self:self._default_end_date())

    def _default_start_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                start_date=r.date_from
            return start_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    start_date=rr.date_from
                return start_date

    def _default_end_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                end_date=r.date_to
            return end_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    end_date=rr.date_to
                return end_date

    def _default_period(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                time_frame=r.id
            return time_frame
    def _default_fiscal_year(self):
        today_date=datetime.now()
        rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                fs_year=r.id
            return fs_year

    @api.onchange('period')
    def _onchange_period(self):
        if self.period:
            self.date_from=self.period.date_from
            self.date_to=self.period.date_to
            self.fiscal_year = self.period.fiscal_year


class Cash_Flow_Report_update(models.TransientModel):
    _name = "cash.flow.report"
    _inherit = "cash.flow.report"
    date_from = fields.Date(string='Date Start',default=lambda self:self._default_start_date())
    date_to = fields.Date(string='Date End',default=lambda self:self._default_end_date())

    fiscal_year=fields.Many2one('fiscal.year',"Fiscal Year",default=lambda self:self._default_fiscal_year())
    period= fields.Many2one('reconciliation.time.fream',"Period",default=lambda self:self._default_period())


    def _default_start_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                start_date=r.date_from
            return start_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    start_date=rr.date_from
                return start_date

    def _default_end_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                end_date=r.date_to
            return end_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    end_date=rr.date_to
                return end_date

    def _default_period(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                time_frame=r.id
            return time_frame
    def _default_fiscal_year(self):
        today_date=datetime.now()
        rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                fs_year=r.id
            return fs_year

    @api.onchange('period')
    def _onchange_period(self):
        if self.period:
            self.date_from=self.period.date_from
            self.date_to=self.period.date_to
            self.fiscal_year = self.period.fiscal_year

class AccountPartnerLedgerUpdate(models.TransientModel):
    _name = "account.report.partner.ledger"
    _inherit = "account.report.partner.ledger"

    date_from = fields.Date(string='Date Start',default=lambda self:self._default_start_date())
    date_to = fields.Date(string='Date End',default=lambda self:self._default_end_date())

    fiscal_year=fields.Many2one('fiscal.year',"Fiscal Year",default=lambda self:self._default_fiscal_year())
    period= fields.Many2one('reconciliation.time.fream',"Period",default=lambda self:self._default_period())

    def _default_start_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                start_date=r.date_from
            return start_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    start_date=rr.date_from
                return start_date

    def _default_end_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                end_date=r.date_to
            return end_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    end_date=rr.date_to
                return end_date

    def _default_period(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                time_frame=r.id
            return time_frame
    def _default_fiscal_year(self):
        today_date=datetime.now()
        rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                fs_year=r.id
            return fs_year

    @api.onchange('period')
    def _onchange_period(self):
        if self.period:
            self.date_from=self.period.date_from
            self.date_to=self.period.date_to
            self.fiscal_year = self.period.fiscal_year



class AccountPartnerLedgerUpdate(models.TransientModel):
    _name = "account.report.general.ledger"
    _inherit = "account.report.general.ledger"

    date_from = fields.Date(string='Date Start',default=lambda self:self._default_start_date())
    date_to = fields.Date(string='Date End',default=lambda self:self._default_end_date())

    fiscal_year=fields.Many2one('fiscal.year',"Fiscal Year",default=lambda self:self._default_fiscal_year())
    period= fields.Many2one('reconciliation.time.fream',"Period",default=lambda self:self._default_period())

    def _default_start_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                start_date=r.date_from
            return start_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    start_date=rr.date_from
                return start_date

    def _default_end_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                end_date=r.date_to
            return end_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    end_date=rr.date_to
                return end_date

    def _default_period(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                time_frame=r.id
            return time_frame
    def _default_fiscal_year(self):
        today_date=datetime.now()
        rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                fs_year=r.id
            return fs_year

    @api.onchange('period')
    def _onchange_period(self):
        if self.period:
            self.date_from=self.period.date_from
            self.date_to=self.period.date_to
            self.fiscal_year = self.period.fiscal_year


class AccountBalanceReportUpdate(models.TransientModel):
    _name = 'account.balance.report'
    _inherit = 'account.balance.report'


    date_from = fields.Date(string='Date Start',default=lambda self:self._default_start_date())
    date_to = fields.Date(string='Date End',default=lambda self:self._default_end_date())

    fiscal_year=fields.Many2one('fiscal.year',"Fiscal Year",default=lambda self:self._default_fiscal_year())
    period= fields.Many2one('reconciliation.time.fream',"Period",default=lambda self:self._default_period())

    def _default_start_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                start_date=r.date_from
            return start_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    start_date=rr.date_from
                return start_date

    def _default_end_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                end_date=r.date_to
            return end_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    end_date=rr.date_to
                return end_date

    def _default_period(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                time_frame=r.id
            return time_frame
    def _default_fiscal_year(self):
        today_date=datetime.now()
        rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                fs_year=r.id
            return fs_year

    @api.onchange('period')
    def _onchange_period(self):
        if self.period:
            self.date_from=self.period.date_from
            self.date_to=self.period.date_to
            self.fiscal_year = self.period.fiscal_year



class AccountTaxReportUpdate(models.TransientModel):
    _name = 'account.tax.report'
    _inherit = 'account.tax.report'
 

    date_from = fields.Date(string='Date Start',default=lambda self:self._default_start_date())
    date_to = fields.Date(string='Date End',default=lambda self:self._default_end_date())

    fiscal_year=fields.Many2one('fiscal.year',"Fiscal Year",default=lambda self:self._default_fiscal_year())
    period= fields.Many2one('reconciliation.time.fream',"Period",default=lambda self:self._default_period())

    def _default_start_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                start_date=r.date_from
            return start_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    start_date=rr.date_from
                return start_date

    def _default_end_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                end_date=r.date_to
            return end_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    end_date=rr.date_to
                return end_date

    def _default_period(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                time_frame=r.id
            return time_frame
    def _default_fiscal_year(self):
        today_date=datetime.now()
        rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                fs_year=r.id
            return fs_year

    @api.onchange('period')
    def _onchange_period(self):
        if self.period:
            self.date_from=self.period.date_from
            self.date_to=self.period.date_to
            self.fiscal_year = self.period.fiscal_year

class AccountPrintReportUpdate(models.TransientModel):
    _name = 'account.print.journal'
    _inherit = 'account.print.journal'



    date_from = fields.Date(string='Date Start',default=lambda self:self._default_start_date())
    date_to = fields.Date(string='Date End',default=lambda self:self._default_end_date())

    fiscal_year=fields.Many2one('fiscal.year',"Fiscal Year",default=lambda self:self._default_fiscal_year())
    period= fields.Many2one('reconciliation.time.fream',"Period",default=lambda self:self._default_period())

    def _default_start_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                start_date=r.date_from
            return start_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    start_date=rr.date_from
                return start_date

    def _default_end_date(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<=',today_date),('date_to','>',today_date)],limit=1)
        if rec:
            for r in rec:
                end_date=r.date_to
            return end_date
        else:
            fs_rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
            if fs_rec:
                for rr in fs_rec:
                    end_date=rr.date_to
                return end_date

    def _default_period(self):
        today_date=datetime.now()
        rec=self.env['reconciliation.time.fream'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                time_frame=r.id
            return time_frame
    def _default_fiscal_year(self):
        today_date=datetime.now()
        rec=self.env['fiscal.year'].search([('date_from','<',today_date),('date_to','>=',today_date)],limit=1)
        if rec:
            for r in rec:
                fs_year=r.id
            return fs_year

    @api.onchange('period')
    def _onchange_period(self):
        if self.period:
            self.date_from=self.period.date_from
            self.date_to=self.period.date_to
            self.fiscal_year = self.period.fiscal_year
