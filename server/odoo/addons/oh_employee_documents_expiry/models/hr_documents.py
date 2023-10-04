from odoo import models, fields ,api


class HrDocument(models.Model):
    _name = 'hr.document'
    _description = 'Documents Template '

    name = fields.Char(string='Document Name', required=True,readonly=True, copy=False, help='You can give your'
                                                                               'Document name here.',default="New",translate=True)
    note = fields.Text(string='Note', copy=False, help="Note",translate=True)
    attach_id = fields.Many2many('ir.attachment', 'attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                 help='You can attach the copy of your document', copy=False)

    @api.model
    def create(self, vals):

    
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.document.sequence')
    
        request = super(HrDocument, self).create(vals)
        return request
        