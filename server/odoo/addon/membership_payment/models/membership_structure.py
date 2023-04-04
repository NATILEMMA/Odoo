from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class MembershipStructure(models.Model):
    _name = "membership.structure"

    _parent_name = "parent_id_2"

    name = fields.Char(required=True, string="Name", translate=True, copy=False, index=True)
    parent_id_2 = fields.Many2one('membership.structure', string="Structure", copy=False, index=True)
    cell = fields.Many2one('member.cells', string="cell", copy=False, index=True)
    main_office = fields.Many2one('main.office', string="main_office", copy=False, index=True)
    wereda = fields.Many2one('membership.handlers.branch', string="wereda", copy=False, index=True)
    sub_city = fields.Many2one('membership.handlers.parent', string="sub city", copy=False, index=True)
    is_member = fields.Boolean("membership structure")
    is_league = fields.Boolean("league structure")
    is_supporter = fields.Boolean("league structure")


class Partner(models.Model):
    _inherit = 'res.partner'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('membership.structure', string="Structure", store=True)

    @api.model
    def create(self, vals):
        res = super(Partner, self).create(vals)
        try:
            if vals['wereda_id']:
                woreda_ia = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
                par = self.env['membership.structure'].search(
                    [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                par_2 = self.env['league.structure'].search(
                    [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                res.struc = par.id
                res.struc_2 = par_2.id
        except:
            return res
        return res

    def write(self, vals):
        try:
           print("try",vals)
           if vals['member_cells']:
             print("vals['member_cell']", vals['member_cells'])
             cell = self.env['membership.structure'].search([('cell', '=', vals['member_cells'])])
             cell_2 = self.env['league.structure'].search([('cell', '=', vals['member_cells'])])
             self.struc = cell.id
             self.struc_2 = cell_2.id
             print("self.struc",self.struc,"self.struc_2",self.struc)
        except:
            try:
                if vals['wereda_id']:
                    woreda_ia = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
                    print("woreda_ia", woreda_ia.id, woreda_ia.name)
                    par = self.env['membership.structure'].search([('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                    par_2 = self.env['league.structure'].search([('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                    print("par",par,par_2)
                    self.struc = par.id
                    self.struc_2 = par_2.id
            except:
                return super(Partner, self).write(vals)
        return super(Partner, self).write(vals)



class Cells(models.Model):
    _inherit = 'member.cells'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('league.structure', string="Structure", store=True)

    @api.model
    def create(self, vals):
        sub = self.env['main.office'].search([('id', '=', vals['main_office'])], limit=1)
        par_1 = self.env['membership.structure'].search([('name', '=', vals['name']), ('main_office', '=', sub.id)])
        wereda = super(Cells, self).create(vals)
        if not par_1:
            par = self.env['membership.structure'].search([('name', '=', sub.name)], limit=1)
            par_2 = self.env['league.structure'].search([('name', '=', sub.name)], limit=1)
            val = {
                'name': vals['name'],
                'parent_id_2': par.id,
                'main_office': vals['main_office'],
                'cell': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }
            val_3 = {
                'name': vals['name'],
                'parent_id_2': par_2.id,
                'main_office': vals['main_office'],
                'cell': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }
            if vals['for_which_members'] == 'member':
                res = self.env['membership.structure'].sudo().create(val)
                wereda.struc = res.id

            else:
                res_3 = self.env['league.structure'].sudo().create(val_3)
                wereda.struc_2 = res_3.id
        return wereda

    def write(self, vals):
        try:
            if vals['name']:
                self.struc.write({'name': vals['name']})
                self.struc_2.write({'name': vals['name']})
        except:
            try:
                if vals['woreda_id']:
                    sun = self.env['main.office'].search([('id', '=', vals['main_office'])])
                    par = self.env['membership.structure'].search([('name', '=', sun.name)])
                    par_2 = self.env['league.structure'].search([('name', '=', sun.name)])
                    self.struc.write({'parent_id_2': par})
                    self.struc_2.write({'parent_id_2': par_2})

            except:
                return super(Cells, self).write(vals)

        return super(Cells, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.for_which_members == 'member':
                if rec.struc:
                    par = self.env['membership.structure'].search([('id', '=', rec.struc.id)])
                    par.unlink()
                else:
                    if rec.struc_2:
                        par = self.env['league.structure'].search([('id', '=', rec.struc_2.id)])
                        par.unlink()
        return super(Cells, self).unlink()


class MembershipHandlersParent(models.Model):
    _inherit = 'membership.handlers.parent'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_3 = fields.Many2one('supporter.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('league.structure', string="Structure", store=True)

    @api.model
    def create(self, vals):
        par_1 = self.env['membership.structure'].search([('name', '=', vals['name'])])
        wereda = super(MembershipHandlersParent, self).create(vals)
        if not par_1:
            val = {
                'name': vals['name'],
                'sub_city': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }
            val_2 = {
                'name': vals['name'],
                'sub_city': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }
            val_3 = {
                'name': vals['name'],
                'sub_city': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }

            res = self.env['membership.structure'].sudo().create(val)
            res_2 = self.env['supporter.structure'].sudo().create(val_2)
            res_3 = self.env['league.structure'].sudo().create(val_3)
            print("val_2", res_2, val_2)
            print("val_3", res_3, val_3)
            wereda.struc = res.id
            wereda.struc_3 = res_2.id
            wereda.struc_2 = res_3.id
        return wereda

    def write(self, vals):
        try:
            if vals['name']:
                self.struc.write({'name': vals['name']})
                self.struc_2.write({'name': vals['name']})
                self.struc_3.write({'name': vals['name']})
                return super(MembershipHandlersParent, self).write(vals)
        except:
            return super(MembershipHandlersParent, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.struc:
                par = self.env['membership.structure'].search([('id', '=', rec.struc.id)])
                par.unlink()
            if rec.struc_2:
                if rec.struc_2:
                    par = self.env['league.structure'].search([('id', '=', rec.struc_2.id)])
                    par.unlink()
            if rec.struc_3:
                if rec.struc_3:
                    par = rec.env['supporter.structure'].search([('id', '=', rec.struc_3.id)])
                    par.unlink()
        return super(MembershipHandlersParent, self).unlink()


class MembershipHandlersChild(models.Model):
    _inherit = 'membership.handlers.branch'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_3 = fields.Many2one('supporter.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('league.structure', string="Structure", store=True)

    @api.model
    def create(self, vals):
        sub = self.env['membership.handlers.parent'].search([('id', '=', vals['parent_id'])], limit=1)
        par_1 = self.env['membership.structure'].search([('name', '=', vals['name']), ('sub_city', '=', sub.id)])
        wereda = super(MembershipHandlersChild, self).create(vals)
        if not par_1:
            par = self.env['membership.structure'].search([('name', '=', sub.name)], limit=1)
            par_3 = self.env['supporter.structure'].search([('name', '=', sub.name)], limit=1)
            par_2 = self.env['league.structure'].search([('name', '=', sub.name)], limit=1)
            val = {
                'name': vals['name'],
                'sub_city': vals['parent_id'],
                'parent_id_2': par.id,
                'wereda': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }
            val_2 = {
                'name': vals['name'],
                'sub_city': vals['parent_id'],
                'parent_id_2': par_3.id,
                'wereda': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }
            val_3 = {
                'name': vals['name'],
                'sub_city': vals['parent_id'],
                'parent_id_2': par_2.id,
                'wereda': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }

            res = self.env['membership.structure'].sudo().create(val)
            res_2 = self.env['supporter.structure'].sudo().create(val_2)
            res_3 = self.env['league.structure'].sudo().create(val_3)
            print("val_2", res_2, val_2)
            print("val_3", res_3, val_3)
            wereda.struc = res.id
            wereda.struc_3 = res_2.id
            wereda.struc_2 = res_3.id
        return wereda

    def write(self, vals):
        try:
            if vals['name']:
                self.struc.write({'name': vals['name']})
                self.struc_2.write({'name': vals['name']})
                self.struc_3.write({'name': vals['name']})
        except:
            try:
                if vals['parent_id']:
                    sun = self.env['membership.handlers.parent'].search([('id', '=', vals['parent_id'])])
                    par = self.env['membership.structure'].search([('name', '=', sun.name)])
                    par_2 = self.env['membership.structure'].search([('name', '=', sun.name)])
                    par_3 = self.env['league.structure'].search([('name', '=', sun.name)])
                    self.struc.write({'parent_id_2': par})
                    self.struc_2.write({'parent_id_2': par_2})
                    self.struc_3.write({'parent_id_2': par_3})
            except:
                return super(MembershipHandlersChild, self).write(vals)

        return super(MembershipHandlersChild, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.struc:
                par = self.env['membership.structure'].search([('id', '=', rec.struc.id)])
                par.unlink()
            if rec.struc_2:
                if rec.struc_2:
                    par = rec.env['league.structure'].search([('id', '=', rec.struc_2.id)])
                    par.unlink()
            if rec.struc_3:
                if rec.struc_3:
                    par = rec.env['supporter.structure'].search([('id', '=', rec.struc_3.id)])
                    par.unlink()
        return super(MembershipHandlersChild, rec).unlink()


class MainOffice(models.Model):
    _inherit = 'main.office'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('league.structure', string="Structure", store=True)

    def unlink(self):
        for rec in self:
            if rec.for_which_members == 'member':
                if rec.struc:
                    par = self.env['membership.structure'].search([('id', '=', rec.struc.id)])
                    par.unlink()
                else:
                    if rec.struc_2:
                        par = self.env['league.structure'].search([('id', '=', rec.struc_2.id)])
                        par.unlink()
        return super(MainOffice, self).unlink()

    @api.model
    def create(self, vals):
        sub = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])], limit=1)
        par_1 = self.env['membership.structure'].search([('name', '=', vals['name']), ('wereda', '=', sub.id)])
        wereda = super(MainOffice, self).create(vals)
        if not par_1:
            par = self.env['membership.structure'].search([('name', '=', sub.name)], limit=1)
            par_2 = self.env['league.structure'].search([('name', '=', sub.name)], limit=1)
            val = {
                'name': vals['name'],
                'parent_id_2': par.id,
                'wereda': vals['wereda_id'],
                'main_office': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }
            val_3 = {
                'name': vals['name'],
                'parent_id_2': par_2.id,
                'main_office': wereda.id,
                'wereda': vals['wereda_id'],
                'is_member': True,
                'is_league': True,
                'is_supporter': True,

            }
            if vals['for_which_members'] == 'member':
                res = self.env['membership.structure'].sudo().create(val)
                wereda.struc = res.id
            else:
                res_3 = self.env['league.structure'].sudo().create(val_3)
                wereda.struc_2 = res_3.id

        return wereda

    def write(self, vals):
        try:
            if vals['name']:
                self.struc.write({'name': vals['name']})
                self.struc_2.write({'name': vals['name']})
        except:
            try:
                try:
                    if vals['woreda_id']:
                        sun = self.env['membership.handlers.branch'].search([('id', '=', vals['woreda_id'])])
                        par = self.env['membership.structure'].search([('name', '=', sun.name)])
                        par_2 = self.env['league.structure'].search([('name', '=', sun.name)])
                        if self.struc:
                            self.struc.write({'parent_id_2': par})
                        if self.struc_2:
                            self.struc_2.write({'parent_id_2': par_2})
                except:
                    if vals['for_which_members']:
                        if vals['for_which_members'] == 'member':
                            sun = self.env['membership.handlers.branch'].search([('id', '=', vals['woreda_id'])])
                            par = self.env['membership.structure'].search([('name', '=', sun.name)])
                            self.struc.write({'parent_id_2': par})

                        else:
                            sun = self.env['membership.handlers.branch'].search([('id', '=', vals['woreda_id'])])
                            par = self.env['league.structure'].search([('name', '=', sun.name)])
                            self.struc.write({'parent_id_2': par})


            except:
                return super(MainOffice, self).write(vals)

        return super(MainOffice, self).write(vals)
