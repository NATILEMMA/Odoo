"""This file will deal with the archiving members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
import base64
    

class CreateAttachment(models.TransientModel):
    _name="attachment.wizard"
    _description="This model will handle the archiving of members"

    name = fields.Char(translate=True)
    res_model = fields.Char()
    res_id = fields.Many2oneReference('Resource ID', model_field='res_model')
    attachment_type = fields.Many2one('attachment.type')
    description = fields.Text('Description')
    type = fields.Selection([('url', 'URL'), ('binary', 'File')])
    datas = fields.Binary()


    def action_done(self):
        """This function will be the action for wizards"""
        wizard = self.env['attachment.wizard'].search([('id', '=', self.id)])
        if self.name and self.attachment_type and self.datas:
            attachment = self.env['ir.attachment'].sudo().create({
                'name': self.name,
                'res_model': wizard.res_model,
                'res_id': wizard.res_id,
                'attachment_type': self.attachment_type.id,
                'description': self.description,
                'type': 'binary',
                'datas': self.datas
            })
        else:
            raise UserError(_("Please Add All The Given Fields"))