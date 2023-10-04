# Copyright 2019 Komit <https://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from email_validator import (
        validate_email,
        EmailSyntaxError,
        EmailUndeliverableError,
    )
except ImportError:
    _logger.debug('Cannot import "email_validator".')

    validate_email = None


class ResPartner(models.Model):
    _inherit = "res.partner"

    def copy_data(self, default=None):
        res = super(ResPartner, self).copy_data(default=default)
        if self._should_filter_duplicates():
            for copy_vals in res:
                copy_vals.pop("email", None)
        return res

    @api.model
    def email_check(self, emails):
        return ",".join(
            self._normalize_email(email.strip())
            for email in emails.split(",")
            if email.strip()
        )

    @api.constrains("email")
    def _check_email_unique(self):
        if self._should_filter_duplicates():
            for rec in self.filtered("email"):
                if "," in rec.email:
                    raise UserError(
                        _(
                            "Field contains multiple email addresses. This is "
                            "not supported when duplicate email addresses are "
                            "not allowed."
                        )
                    )
                if self.search_count([("email", "=", rec.email), ("id", "!=", rec.id)]):
                    raise UserError(
                        _("Email '%s' is already in use.") % rec.email.strip()
                    )

    def _normalize_email(self, email):
        if not self._should_check_syntax():
            return email
        if validate_email is None:
            _logger.warning(
                "Can not validate email, "
                'python dependency required "email_validator"'
            )
            return email

        try:
            result = validate_email(
                email, check_deliverability=self._should_check_deliverability(),
            )
        except EmailSyntaxError:
            raise ValidationError(_("%s is an invalid email") % email.strip())
        except EmailUndeliverableError:
            raise ValidationError(
                _("Cannot deliver to email address %s") % email.strip()
            )
        return result["local"].lower() + "@" + result["domain_i18n"]

    def _should_check_syntax(self):
        return self.env.company.partner_email_check_syntax

    def _should_filter_duplicates(self):
        return self.env.company.partner_email_check_filter_duplicates

    def _should_check_deliverability(self):
        return self.env.company.partner_email_check_check_deliverability

    @api.model
    def create(self, vals):
        if vals.get("email"):
            vals["email"] = self.email_check(vals["email"])
        if vals.get("mobile"):
            for st in vals['mobile']:
               if not st.isdigit():
                    print('st', st)
                    if str(st) != '+':
                        raise UserError(_("You Can not Have Characters in a mobile Number"))
                    if vals['mobile'][0] != '0':
                        if str(vals['mobile'][0]) != '+':
                            raise UserError(_("A Valid mobile Number Starts With 0 or +"))
                    if len(vals['mobile']) != 10:
                        if len(vals['mobile']) != 13:
                            raise UserError(_("A Valid mobile Number Has 10 Digits"))
               if vals.get("country_id"):
                    country = self.env['res.country'].search([('id', '=', vals['country_id'])])
                    if len(vals['mobile']) == 10:
                        my_string = vals['mobile'][1:]
                    if len(vals['mobile']) == 13:
                        my_string = vals['mobile'][3:]
                    mobile = '+' + str(country.phone_code) + str(my_string)
                    vals['mobile'] = mobile

            if not vals.get("country_id"):
                    if len(vals['mobile']) == 10:
                        my_string = vals['mobile'][1:]
                    if len(vals['mobile']) == 13:
                        my_string = vals['mobile'][3:]
                    mobile = '+251'+ str(my_string)
                    vals['mobile'] = mobile
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        if vals.get("email"):
            vals["email"] = self.email_check(vals["email"])
        if vals.get("mobile"):
            for record in self:
                if record.mobile:
                    for st in vals['mobile']:
                        if not st.isdigit():
                          print('st', st)
                          if str(st) != '+':
                            raise UserError(_("You Can not Have Characters in a mobile Number"))
                    if vals['mobile'][0] != '0':
                        if str(vals['mobile'][0]) != '+':
                           raise UserError(_("A Valid mobile Number Starts With 0 or +"))
                    if len(vals['mobile']) != 10:
                         if len(vals['mobile']) != 13:
                            raise UserError(_("A Valid mobile Number Has 10 Digits"))
                if vals.get("country_id"):
                    country = self.env['res.country'].search([('id', '=', vals['country_id'])])
                    if len(vals['mobile']) == 10:
                      my_string = vals['mobile'][1:]
                    if len(vals['mobile']) == 13:
                        my_string = vals['mobile'][4:]
                    mobile = '+' + str(country.phone_code) + str(my_string)
                    vals['mobile'] = mobile
                if self.country_id:
                    country = self.env['res.country'].search([('id', '=', self.country_id.id)])
                    if len(vals['mobile']) == 10:
                      my_string = vals['mobile'][1:]
                    if len(vals['mobile']) == 13:
                        my_string = vals['mobile'][4:]
                    mobile = '+' + str(country.phone_code) + str(my_string)
                    vals['mobile'] = mobile
                if not self.country_id and not vals.get("country_id"):
                    if len(vals['mobile']) == 10:
                      my_string = vals['mobile'][1:]
                    if len(vals['mobile']) == 13:
                        my_string = vals['mobile'][4:]
                    mobile = '+251' + str(my_string)
                    vals['mobile'] = mobile
        if vals.get("country_id") and not vals.get("mobile"):
            country = self.env['res.country'].search([('id', '=', vals['country_id'])])
            my_string = ''
            if len(self.mobile) == 11:
                my_string = self.mobile[1:]
            if len(self.mobile) == 14:
                my_string = self.mobile[4:]
            mobile = '+' + str(country.phone_code) + str(my_string)
            if my_string != '':
              vals['mobile'] = mobile

        return super(ResPartner, self).write(vals)
