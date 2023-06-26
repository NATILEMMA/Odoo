from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    additional_phone = fields.Char(string='Additional Phone')
    additional_website = fields.Char(string='Additional Website')
    building = fields.Char(string='Currently working Building')
    floor = fields.Integer(string='Floor')
    whatsapp = fields.Char(string='Whatsapp Number')

