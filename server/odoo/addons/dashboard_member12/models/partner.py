# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from datetime import date
# from odoo import api, fields, models, _
# from odoo.exceptions import UserError, ValidationError
# import hashlib
# import logging
# _logger = logging.getLogger(__name__)




# class Partner(models.Model):
#     _inherit = 'res.partner'


#     member_password_verfiy =  fields.Boolean(string="Verfiy User", default="f")

#     def action_portal_reset_member_password(self):
#         for record in self:
#             _logger.info("#####$$$$$$$$$$$$$$$$")
#             _logger.info(record.id)
#             # partner = self.env['res.partner'].sudo().search([('id','=', self.id)], limit=1)
#             res = self.env['res.users'].sudo().search([('partner_id','=', record.id)], limit=1)
        
#             # salt = "5gz"
#             # # Hashing the password
#             password = "123456"
#             # dataBase_password = password+salt
#             # _logger.info(dataBase_password)
#             # hashed = hashlib.md5(dataBase_password.encode())
#             # _logger.info(hashed)

#             _logger.info("###### member_password_verfiy %s", record.member_password_verfiy)
#             res.sudo().update({
#                 'password': password
#             })
#             record.update({
#                 'member_password_verfiy': False
#             })
#             user = self.env.user
#             message = "The User Name For " + str(record.name) + " Is " + str(record.user_name) + ", password is 123456. Please Advise The Member To Change This Passport After They Login." 
#             user.notify_success(message, '<h4>User Name</h4>', True)           
    