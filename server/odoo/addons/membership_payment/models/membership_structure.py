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
    users = fields.Many2many(
        comodel_name="res.users",
        relation="structure_group_users_rel",
        column1="gid",
        column2="uid",
        string=" Users",
        auto_join=True,
        store=True,
    )

    def give_structure(self):

        sub_city = self.env['membership.handlers.parent'].search([])
        for sub in sub_city:
            par = self.env['membership.structure'].search([('name', '=', sub.name)])
            user = []
            user.append(sub.parent_manager.id)
            for line in sub.city_id.city_manager:
                user.append(line.id)
            if not par:
                vals = {
                    'name': sub.name,
                    'sub_city': sub.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,
                    'users': [(6, 0, user)],
                }
                res = self.env['membership.structure'].sudo().create(vals)
                sub.struc = res.id

        wereda = self.env['membership.handlers.branch'].search([])
        for wor in wereda:
            par_1 = self.env['membership.structure'].search(
                [('name', '=', wor.name), ('sub_city', '=', wor.parent_id.id)])
            if not par_1:
                par = self.env['membership.structure'].search([('name', '=', wor.parent_id.name)], limit=1)
                user = []
                for line in wor.parent_id.city_id.city_manager:
                    user.append(line.id)
                user.append(wor.parent_id.parent_manager.id)
                user.append(wor.branch_manager.id)
                vals = {
                    'name': wor.name,
                    'sub_city': wor.parent_id.id,
                    'parent_id_2': par.id,
                    'wereda': wor.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,
                    'users': [(6, 0, user)],

                }
                res = self.env['membership.structure'].sudo().create(vals)
                wor.struc = res.id

        main_office = self.env['main.office'].search([])
        for main in main_office:
            par_2 = self.env['membership.structure'].search(
                [('name', '=', main.name), ('wereda', '=', main.wereda_id.id),
                 ('sub_city', '=', main.wereda_id.parent_id.id)])
            if not par_2:
                par = self.env['membership.structure'].search(
                    [('sub_city', '=', main.wereda_id.parent_id.id), ('wereda', '=', main.wereda_id.id),
                     ('name', '=', main.wereda_id.name)])
                user = []
                for line in main.wereda_id.parent_id.city_id.city_manager:
                    user.append(line.id)
                user.append(main.wereda_id.parent_id.parent_manager.id)
                user.append(main.wereda_id.branch_manager.id)

                if main.for_which_members == 'member':
                    vals = {
                        'name': main.name,
                        'sub_city': main.wereda_id.parent_id.id,
                        'parent_id_2': par.id,
                        'wereda': main.wereda_id.id,
                        'main_office': main.id,
                        'is_member': True,
                        'users': [(6, 0, user)]

                    }
                    res = self.env['membership.structure'].sudo().create(vals)
                    main.struc = res.id
        cells = self.env['member.cells'].search([])
        for cell in cells:
            if cell.main_office:
                cell_main_office = cell.main_office

            par_2 = self.env['membership.structure'].search(
                [('name', '=', cell.name), ('main_office', '=', cell_main_office.id),
                 ('wereda', '=', cell.wereda_id.id), ('sub_city', '=', cell.wereda_id.parent_id.id)])
            if not par_2:
                par = self.env['membership.structure'].search(
                    [('name', '=', cell_main_office.name), ('main_office', '=', cell.main_office.id),
                     ('wereda', '=', cell.wereda_id.id), ('sub_city', '=', cell.wereda_id.parent_id.id)])
                if cell.main_office:
                    user = []
                    for line in cell.main_office.wereda_id.parent_id.city_id.city_manager:
                        user.append(line.id)
                    user.append(cell.main_office.wereda_id.parent_id.parent_manager.id)
                    user.append(cell.main_office.wereda_id.branch_manager.id)
                    vals = {
                        'name': cell.name,
                        'sub_city': cell_main_office.wereda_id.parent_id.id,
                        'parent_id_2': par.id,
                        'wereda': cell_main_office.wereda_id.id,
                        'main_office': cell_main_office.id,
                        'cell': cell.id,
                        'is_member': True,
                        'users': [(6, 0, user)]

                    }
                    res = self.env['membership.structure'].sudo().create(vals)
                    cell.struc = res.id

            partner = self.env['res.partner'].search([])
            candidate = self.env['candidate.members'].search([])
            supporter = self.env['supporter.members'].search([])
            for part in partner:
                if part.member_cells:
                    par_2 = self.env['membership.structure'].search([('cell', '=', part.member_cells.id)])
                    for line_2 in par_2:
                        part.struc = line_2.id
                if part.wereda_id and not part.member_cells and not part.struc:
                    par_3 = self.env['membership.structure'].search(
                        [('wereda', '=', part.wereda_id.id), ('name', '=', part.wereda_id.name)])
                    for line in par_3:
                        part.struc = par_3.id
            for cand in candidate:
                if cand.wereda_id:
                    par_2 = self.env['membership.structure'].search(
                        [('wereda', '=', part.wereda_id.id), ('name', '=', part.wereda_id.name)])
                    cand.struc = par_2.id

            for supp in supporter:
                if supp.wereda_id:
                    par_2 = self.env['membership.structure'].search(
                        [('wereda', '=', part.wereda_id.id), ('name', '=', part.wereda_id.name)])
                    supp.struc = par_2.id


class Partner(models.Model):
    _inherit = 'res.partner'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('league.structure', string="Structure", store=True)

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
            print("try", vals)
            if vals['member_cells']:
                print("vals['member_cell']", vals['member_cells'])
                cell = self.env['membership.structure'].search([('cell', '=', vals['member_cells'])])
                cell_2 = self.env['league.structure'].search([('cell', '=', vals['member_cells'])])
                self.struc = cell.id
                self.struc_2 = cell_2.id
                print("self.struc", self.struc, "self.struc_2", self.struc)
        except:
            try:
                if vals['wereda_id']:
                    woreda_ia = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
                    print("woreda_ia", woreda_ia.id, woreda_ia.name)
                    par = self.env['membership.structure'].search(
                        [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                    par_2 = self.env['league.structure'].search(
                        [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                    print("par", par, par_2)
                    self.struc = par.id
                    self.struc_2 = par_2.id
            except:
                return super(Partner, self).write(vals)
        return super(Partner, self).write(vals)


class Cells(models.Model):
    _inherit = 'member.cells'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('league.structure', string="Structure", store=True)

    def update_translation_member_cells(self):
        current_lang = self.env.context.get('lang')
        self = self.with_context(lang='en_US')
        eng_name = self.name
        self.struc.name = eng_name
        self.struc_2.name = eng_name
        self = self.with_context(lang='am_ET')
        amh_name = self.name
        self.struc.name = amh_name
        self.struc_2.name = amh_name
        self = self.with_context(lang='current_lang')

    @api.model
    def create(self, vals):
        print("create")
        try:
           try:
             sub = self.env['main.office'].search([('id', '=', vals['main_office'])], limit=1)
             sub_2 = self.env['main.office'].search([('id', '=', vals['main_office_league'])], limit=1)
           except:
             sub_2 = False
             sub = self.env['main.office'].search([('id', '=', vals['main_office'])], limit=1)
        except:
            sub = True
            sub_2 = self.env['main.office'].search([('id', '=', vals['main_office_league'])], limit=1)

        par_1 = self.env['membership.structure'].search([('name', '=', vals['name']), ('main_office', '=', sub.id)])
        wereda = super(Cells, self).create(vals)
        print("par", par_1)
        user = self.env.user
        config = self.env['cell.configuration'].search([('for_members_or_leagues', '=', wereda.for_which_members)])
        if config:
            if wereda.total < config.minimum_number:
                warning_message = "The Added Numbers Of Members Is " + str(wereda.total) + " Which Is Less Than " + str(
                    config.minimum_number) + " According To The Rule Given."
                if config.reject:
                    raise UserError(_(warning_message))
                else:
                    user.notify_warning(warning_message, '<h4>Minimum Number of Members not Reached.</h4>', True)
            elif wereda.total > config.maximum_number:
                if config.reject:
                    message = "The Added Numbers Of Members Is " + str(wereda.total) + " Which Is More Than " + str(
                        config.maximum_number) + " According To The Rule Given."
                    raise UserError(_(message))
                else:
                    message = "The Number Of Members You Added Is Going To Exceed The Maximum Number Given In The Rule."
                    user.notify_warning(message, '<h4>Maximum Numbers Of Members Are Exceeding.</h4>', True)
        else:
            raise UserError(_("Please Configure The Number of Members Allowed In A Single Cell"))

        if wereda.for_which_members == 'member':
            user = []
            user.append(wereda.main_office.wereda_id.branch_manager.id)
            user.append(wereda.main_office.wereda_id.parent_id.parent_manager.id)
            for line in wereda.main_office.wereda_id.parent_id.city_id.city_manager:
                user.append(line.id)
            mo = wereda.main_office
            print('mo', mo)

        else:
            user = []
            user.append(wereda.main_office_league.wereda_id.branch_manager.id)
            user.append(wereda.main_office_league.wereda_id.parent_id.parent_manager.id)
            for line in wereda.main_office_league.wereda_id.parent_id.city_id.city_manager:
                user.append(line.id)
            mo = wereda.main_office_league
        print("par_1", par_1.id)
        if not par_1:
            print("is not part", sub.id, sub.name)
            if sub:
                par = self.env['membership.structure'].search([('main_office', '=', sub.id),('name','=', sub.name)], limit=1)
                val = {
                    'name': wereda.name,
                    'parent_id_2': par.id,
                    'main_office': mo.id,
                    'cell': wereda.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,
                    'users': [(6, 0, user)],

                }
            if sub_2:
                print()
                par_2 = self.env['league.structure'].search([('main_office', '=', sub_2.id),('name','=', sub_2.name)], limit=1)
                val_3 = {
                    'name': wereda.name,
                    'parent_id_2': par_2.id,
                    'main_office': mo.id,
                    'cell': wereda.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,
                    'users': [(6, 0, user)],

                }

            if wereda.for_which_members == 'member':
                print("324")
                res = self.env['membership.structure'].sudo().create(val)
                print("res", res)
                wereda.struc = res.id

            else:
                print("vals_3", val_3)
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

    def update_translation_parent(self):
        print("change_langue", self)
        current_lang = self.env.context.get('lang')
        self = self.with_context(lang='en_US')
        eng_name = self.name
        self.struc.name = eng_name
        self.struc_2.name = eng_name
        self.struc_3.name = eng_name
        self = self.with_context(lang='am_ET')
        amh_name = self.name
        self.struc.name = amh_name
        # self.struc_2.name = amh_name
        # self.struc_3.name = amh_name
        self = self.with_context(lang='current_lang')
        print("translation", amh_name, eng_name)
        return

    @api.model
    def create(self, vals):
        par_1 = self.env['membership.structure'].search([('name', '=', vals['name'])])
        wereda = super(MembershipHandlersParent, self).create(vals)
        user = []
        user.append(wereda.parent_manager.id)
        for line in wereda.city_id.city_manager:
            user.append(line.id)
        if not par_1:
            val = {
                'name': vals['name'],
                'sub_city': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,
                'users': [(6, 0, user)],

            }
            val_2 = {
                'name': vals['name'],
                'sub_city': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,
                'users': [(6, 0, user)],

            }
            val_3 = {
                'name': vals['name'],
                'sub_city': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,
                'users': [(6, 0, user)],

            }

            res = self.env['membership.structure'].sudo().create(val)
            res_2 = self.env['supporter.structure'].sudo().create(val_2)
            res_3 = self.env['league.structure'].sudo().create(val_3)
            wereda.struc = res.id
            wereda.struc_3 = res_2.id
            wereda.struc_2 = res_3.id
        return wereda

    def write(self, vals):
        print("sub run")
        try:
            try:
                try:
                    if vals['name']:
                        self.struc.write({'name': vals['name']})
                        self.struc_2.write({'name': vals['name']})
                        self.struc_3.write({'name': vals['name']})
                    if vals['parent_manager']:
                        flag = False
                        for mananager in self.city_id.city_manager:
                            if mananager.id == self.parent_manager.id:
                                flag = True
                        if not flag:
                            par = self.env['membership.structure'].search([('sub_city', '=', self.id)])
                            par_2 = self.env['league.structure'].search([('sub_city', '=', self.id)])
                            par_3 = self.env['supporter.structure'].search([('sub_city', '=', self.id)])
                            for str in par:
                                user = []
                                user.append(vals['parent_manager'])
                                for id in str.users:
                                    if id.id != self.parent_manager.id:
                                        user.append(id.id)
                                str.users = [(6, 0, user)]
                            for str in par_2:
                                user = []
                                user.append(vals['parent_manager'])
                                for id in str.users:
                                    if id.id != self.parent_manager.id:
                                        user.append(id.id)
                                str.users = [(6, 0, user)]
                            for str in par_3:
                                user = []
                                user.append(vals['parent_manager'])
                                for id in str.users:
                                    if id.id != self.parent_manager.id:
                                        user.append(id.id)
                                str.users = [(6, 0, user)]
                        else:
                            par = self.env['membership.structure'].search([('sub_city', '=', self.id)])
                            par_2 = self.env['league.structure'].search([('sub_city', '=', self.id)])
                            par_3 = self.env['supporter.structure'].search([('sub_city', '=', self.id)])
                            for str in par:
                                user = []
                                user.append(vals['parent_manager'])
                            str.users = [(6, 0, user)]
                            for str in par_2:
                                user = []
                                user.append(vals['parent_manager'])
                            str.users = [(6, 0, user)]
                            for str in par_3:
                                user = []
                                user.append(vals['parent_manager'])
                            str.users = [(6, 0, user)]
                    return super(MembershipHandlersParent, self).write(vals)

                except:
                    print("try expect")
                    if vals['name']:
                        self.struc.write({'name': vals['name']})
                        self.struc_2.write({'name': vals['name']})
                        self.struc_3.write({'name': vals['name']})
                        return super(MembershipHandlersParent, self).write(vals)
            except:
                if vals['parent_manager']:
                    flag = False
                    for mananager in self.city_id.city_manager:
                        if mananager.id == self.parent_manager.id:
                            flag = True
                    if not flag:
                        par = self.env['membership.structure'].search([('sub_city', '=', self.id)])
                        par_2 = self.env['league.structure'].search([('sub_city', '=', self.id)])
                        par_3 = self.env['supporter.structure'].search([('sub_city', '=', self.id)])
                        for str in par:
                            user = []
                            user.append(vals['parent_manager'])
                            for id in str.users:
                                if id.id != self.parent_manager.id:
                                    user.append(id.id)
                            str.users = [(6, 0, user)]
                        for str in par_2:
                            user = []
                            user.append(vals['parent_manager'])
                            for id in str.users:
                                if id.id != self.parent_manager.id:
                                    user.append(id.id)
                            str.users = [(6, 0, user)]
                        for str in par_3:
                            user = []
                            user.append(vals['parent_manager'])
                            for id in str.users:
                                if id.id != self.parent_manager.id:
                                    user.append(id.id)
                            str.users = [(6, 0, user)]
                    else:
                        par = self.env['membership.structure'].search([('sub_city', '=', self.id)])
                        par_2 = self.env['league.structure'].search([('sub_city', '=', self.id)])
                        par_3 = self.env['supporter.structure'].search([('sub_city', '=', self.id)])
                        for str in par:
                            user = []
                            user.append(vals['parent_manager'])
                        str.users = [(6, 0, user)]
                        for str in par_2:
                            user = []
                            user.append(vals['parent_manager'])
                        str.users = [(6, 0, user)]
                        for str in par_3:
                            user = []
                            user.append(vals['parent_manager'])
                        str.users = [(6, 0, user)]
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

    def update_translation_branch(self):
        current_lang = self.env.context.get('lang')
        self = self.with_context(lang='en_US')
        eng_name = self.name
        self.struc.name = eng_name
        self = self.with_context(lang='am_ET')
        amh_name = self.name
        self.struc.name = amh_name
        self = self.with_context(lang='current_lang')

    @api.model
    def create(self, vals):
        sub = self.env['membership.handlers.parent'].search([('id', '=', vals['parent_id'])], limit=1)
        par_1 = self.env['membership.structure'].search([('name', '=', vals['name']), ('sub_city', '=', sub.id)])
        wereda = super(MembershipHandlersChild, self).create(vals)
        user = []
        user.append(wereda.branch_manager.id)
        user.append(wereda.parent_id.parent_manager.id)
        for line in wereda.parent_id.city_id.city_manager:
            user.append(line.id)
        if not par_1:
            par = self.env['membership.structure'].search([('name', '=', sub.name)], limit=1)
            par_3 = self.env['supporter.structure'].search([('name', '=', sub.name)], limit=1)
            par_2 = self.env['league.structure'].search([('name', '=', sub.name)], limit=1)
            print("before", par.users, wereda.branch_manager.id)
            arr = par.users.ids
            arr.append(wereda.branch_manager.id)
            par.users = [(6, 0, arr)]
            par_2.users = [(6, 0, arr)]
            par_3.users = [(6, 0, arr)]
            # par.write({'users' : [(6, 0, arr)]})
            # par_2.write({'users' : [(6, 0, arr)]})
            # par_3.write({'users' : [(6, 0, arr)]})
            print("after", par.users)
            # par_2.users = [(6, 0, wereda.branch_manager.ids)]
            # par_3.users = [(6, 0, wereda.branch_manager.ids)]
            val = {
                'name': vals['name'],
                'sub_city': vals['parent_id'],
                'parent_id_2': par.id,
                'wereda': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,
                'users': [(6, 0, user)],

            }
            val_2 = {
                'name': vals['name'],
                'sub_city': vals['parent_id'],
                'parent_id_2': par_3.id,
                'wereda': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,
                'users': [(6, 0, user)],

            }
            val_3 = {
                'name': vals['name'],
                'sub_city': vals['parent_id'],
                'parent_id_2': par_2.id,
                'wereda': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,
                'users': [(6, 0, user)],

            }

            res = self.env['membership.structure'].sudo().create(val)
            res_2 = self.env['supporter.structure'].sudo().create(val_2)
            res_3 = self.env['league.structure'].sudo().create(val_3)
            wereda.struc = res.id
            wereda.struc_3 = res_2.id
            wereda.struc_2 = res_3.id
        return wereda

    def write(self, vals):
        try:
            try:
                if vals['name']:
                    self.struc.write({'name': vals['name']})
                    self.struc_2.write({'name': vals['name']})
                    self.struc_3.write({'name': vals['name']})
                if vals['parent_id']:
                    sun = self.env['membership.handlers.parent'].search([('id', '=', vals['parent_id'])])
                    par = self.env['membership.structure'].search([('name', '=', sun.name)])
                    par_2 = self.env['supporter.structure'].search([('name', '=', sun.name)])
                    par_3 = self.env['league.structure'].search([('name', '=', sun.name)])
                    self.struc.write({'parent_id_2': par})
                    self.struc_2.write({'parent_id_2': par_2})
                    self.struc_3.write({'parent_id_2': par_3})
                if vals['branch_manager']:
                    par = self.env['membership.structure'].search([('wereda', '=', self.id)])
                    par_2 = self.env['supporter.structure'].search([('wereda', '=', self.id)])
                    par_3 = self.env['league.structure'].search([('wereda', '=', self.id)])
                    for str in par:
                        user = []
                        user.append(vals['branch_manager'])
                        for id in str.users:
                            if id.id != self.branch_manager.id:
                                user.append(id.id)
                        str.users = [(6, 0, user)]
                    for str in par_2:
                        user = []
                        user.append(vals['branch_manager'])
                        for id in str.users:
                            if id.id != self.branch_manager.id:
                                user.append(id.id)
                        str.users = [(6, 0, user)]
                    for str in par_3:
                        user = []
                        user.append(vals['branch_manager'])
                        for id in str.users:
                            if id.id != self.branch_manager.id:
                                user.append(id.id)
                        str.users = [(6, 0, user)]
                    print("before the magic happen", self.parent_id.struc.users.ids)
                    if self.parent_id.parent_manager.id != self.branch_manager.id:
                        if self.branch_manager.id not in self.parent_id.city_id.city_manager.ids:
                            arr = []
                            arr_2 = []
                            arr_3 = []
                            arr.append(vals['branch_manager'])
                            arr_2.append(vals['branch_manager'])
                            arr_3.append(vals['branch_manager'])
                            for usr in self.parent_id.struc.users.ids:
                                if usr != self.branch_manager.id:
                                    arr.append(usr)
                            for usr in self.parent_id.struc_2.users.ids:
                                if usr != self.branch_manager.id:
                                    arr_2.append(usr)
                            for usr in self.parent_id.struc_3.users.ids:
                                if usr != self.branch_manager.id:
                                    arr_3.append(usr)
                            self.parent_id.struc.users = [(6, 0, arr)]
                            self.parent_id.struc_2.users = [(6, 0, arr_2)]
                            self.parent_id.struc_3.users = [(6, 0, arr_3)]
                    print("after the magic happen", self.parent_id.struc.users.ids, vals['branch_manager'],
                          self.struc.users.ids)

                return super(MembershipHandlersChild, self).write(vals)
            except:
                try:
                    if vals['name']:
                        self.struc.write({'name': vals['name']})
                        self.struc_2.write({'name': vals['name']})
                        self.struc_3.write({'name': vals['name']})
                    if vals['parent_id']:
                        sun = self.env['membership.handlers.parent'].search([('id', '=', vals['parent_id'])])
                        par = self.env['membership.structure'].search([('name', '=', sun.name)])
                        par_2 = self.env['membership.structure'].search([('name', '=', sun.name)])
                        par_3 = self.env['league.structure'].search([('name', '=', sun.name)])
                        self.struc.write({'parent_id_2': par})
                        self.struc_2.write({'parent_id_2': par_2})
                        self.struc_3.write({'parent_id_2': par_3})
                    return super(MembershipHandlersChild, self).write(vals)
                except:
                    try:
                        if vals['name']:
                            self.struc.write({'name': vals['name']})
                            self.struc_2.write({'name': vals['name']})
                            self.struc_3.write({'name': vals['name']})
                        if vals['branch_manager']:
                            par = self.env['membership.structure'].search([('wereda', '=', self.id)])
                            par_2 = self.env['supporter.structure'].search([('wereda', '=', self.id)])
                            par_3 = self.env['league.structure'].search([('wereda', '=', self.id)])
                            for str in par:
                                user = []
                                user.append(vals['branch_manager'])
                                for id in str.users:
                                    if id.id != self.branch_manager.id:
                                        user.append(id.id)
                                str.users = [(6, 0, user)]
                            for str in par_2:
                                user = []
                                user.append(vals['branch_manager'])
                                for id in str.users:
                                    if id.id != self.branch_manager.id:
                                        user.append(id.id)
                                str.users = [(6, 0, user)]
                            for str in par_3:
                                user = []
                                user.append(vals['branch_manager'])
                                for id in str.users:
                                    if id.id != self.branch_manager.id:
                                        user.append(id.id)
                                str.users = [(6, 0, user)]
                            print("before the magic happen", self.parent_id.struc.users.ids)
                            if self.parent_id.parent_manager.id != self.branch_manager.id:
                                if self.branch_manager.id not in self.parent_id.city_id.city_manager.ids:
                                    arr = []
                                    arr_2 = []
                                    arr_3 = []
                                    arr.append(vals['branch_manager'])
                                    arr_2.append(vals['branch_manager'])
                                    arr_3.append(vals['branch_manager'])
                                    for usr in self.parent_id.struc.users.ids:
                                        if usr != self.branch_manager.id:
                                            arr.append(usr)
                                    for usr in self.parent_id.struc_2.users.ids:
                                        if usr != self.branch_manager.id:
                                            arr_2.append(usr)
                                    for usr in self.parent_id.struc_3.users.ids:
                                        if usr != self.branch_manager.id:
                                            arr_3.append(usr)
                                    self.parent_id.struc.users = [(6, 0, arr)]
                                    self.parent_id.struc_2.users = [(6, 0, arr_2)]
                                    self.parent_id.struc_3.users = [(6, 0, arr_3)]

                            print("after the magic happen", self.parent_id.struc.users.ids, vals['branch_manager'])

                        return super(MembershipHandlersChild, self).write(vals)
                    except:
                        if vals['name']:
                            self.struc.write({'name': vals['name']})
                            self.struc_2.write({'name': vals['name']})
                            self.struc_3.write({'name': vals['name']})
                        return super(MembershipHandlersChild, self).write(vals)
        except:
            print("except 1")
            try:
                print("except try")
                try:
                    if vals['parent_id']:
                        sun = self.env['membership.handlers.parent'].search([('id', '=', vals['parent_id'])])
                        par = self.env['membership.structure'].search([('name', '=', sun.name)])
                        par_2 = self.env['supporter.structure'].search([('name', '=', sun.name)])
                        par_3 = self.env['league.structure'].search([('name', '=', sun.name)])
                        self.struc.write({'parent_id_2': par})
                        self.struc_2.write({'parent_id_2': par_2})
                        self.struc_3.write({'parent_id_2': par_3})
                    if vals['branch_manager']:
                        par = self.env['membership.structure'].search([('wereda', '=', self.id)])
                        par_2 = self.env['supporter.structure'].search([('wereda', '=', self.id)])
                        par_3 = self.env['league.structure'].search([('wereda', '=', self.id)])
                        for str in par:
                            user = []
                            user.append(vals['branch_manager'])
                            for id in str.users:
                                if id.id != self.branch_manager.id:
                                    user.append(id.id)
                            str.users = [(6, 0, user)]
                        for str in par_2:
                            user = []
                            user.append(vals['branch_manager'])
                            for id in str.users:
                                if id.id != self.branch_manager.id:
                                    user.append(id.id)
                            str.users = [(6, 0, user)]
                        for str in par_3:
                            user = []
                            user.append(vals['branch_manager'])
                            for id in str.users:
                                if id.id != self.branch_manager.id:
                                    user.append(id.id)
                            str.users = [(6, 0, user)]
                        print("before the magic happen", self.parent_id.struc.users.ids)
                        if self.parent_id.parent_manager.id != self.branch_manager.id:
                            if self.branch_manager.id not in self.parent_id.city_id.city_manager.ids:
                                arr = []
                                arr_2 = []
                                arr_3 = []
                                arr.append(vals['branch_manager'])
                                arr_2.append(vals['branch_manager'])
                                arr_3.append(vals['branch_manager'])
                                for usr in self.parent_id.struc.users.ids:
                                    if usr != self.branch_manager.id:
                                        arr.append(usr)
                                for usr in self.parent_id.struc_2.users.ids:
                                    if usr != self.branch_manager.id:
                                        arr_2.append(usr)
                                for usr in self.parent_id.struc_3.users.ids:
                                    if usr != self.branch_manager.id:
                                        arr_3.append(usr)
                                self.parent_id.struc.users = [(6, 0, arr)]
                                self.parent_id.struc_2.users = [(6, 0, arr_2)]
                                self.parent_id.struc_3.users = [(6, 0, arr_3)]
                        print("after the magic happen", self.parent_id.struc.users.ids, vals['branch_manager'])

                    return super(MembershipHandlersChild, self).write(vals)
                except:
                    print("except except")
                    try:
                        print("except except try")
                        if vals['parent_id']:
                            sun = self.env['membership.handlers.parent'].search([('id', '=', vals['parent_id'])])
                            par = self.env['membership.structure'].search([('name', '=', sun.name)])
                            par_2 = self.env['supporter.structure'].search([('name', '=', sun.name)])
                            par_3 = self.env['league.structure'].search([('name', '=', sun.name)])
                            self.struc.write({'parent_id_2': par})
                            self.struc_2.write({'parent_id_2': par_2})
                            self.struc_3.write({'parent_id_2': par_3})
                        return super(MembershipHandlersChild, self).write(vals)
                    except:
                        print("except except except")
                        if vals['branch_manager']:
                            par = self.env['membership.structure'].search([('wereda', '=', self.id)])
                            par_2 = self.env['supporter.structure'].search([('wereda', '=', self.id)])
                            par_3 = self.env['league.structure'].search([('wereda', '=', self.id)])
                            for str in par:
                                user = []
                                user.append(vals['branch_manager'])
                                for id in str.users:
                                    if id.id != self.branch_manager.id:
                                        user.append(id.id)
                                str.users = [(6, 0, user)]
                            for str in par_2:
                                user = []
                                user.append(vals['branch_manager'])
                                for id in str.users:
                                    if id.id != self.branch_manager.id:
                                        user.append(id.id)
                                str.users = [(6, 0, user)]
                            for str in par_3:
                                user = []
                                user.append(vals['branch_manager'])
                                for id in str.users:
                                    if id.id != self.branch_manager.id:
                                        user.append(id.id)
                                str.users = [(6, 0, user)]
                            print("before the magic happen", self.parent_id.struc.users.ids)
                            if self.parent_id.parent_manager.id != self.branch_manager.id:
                                if self.branch_manager.id not in self.parent_id.city_id.city_manager.ids:
                                    arr = []
                                    arr_2 = []
                                    arr_3 = []
                                    arr.append(vals['branch_manager'])
                                    arr_2.append(vals['branch_manager'])
                                    arr_3.append(vals['branch_manager'])
                                    for usr in self.parent_id.struc.users.ids:
                                        if usr != self.branch_manager.id:
                                            arr.append(usr)
                                    for usr in self.parent_id.struc_2.users.ids:
                                        if usr != self.branch_manager.id:
                                            arr_2.append(usr)
                                    for usr in self.parent_id.struc_3.users.ids:
                                        if usr != self.branch_manager.id:
                                            arr_3.append(usr)
                                    self.parent_id.struc.users = [(6, 0, arr)]
                                    self.parent_id.struc_2.users = [(6, 0, arr_2)]
                                    self.parent_id.struc_3.users = [(6, 0, arr_3)]
                            print("after the magic happen", self.parent_id.struc.users.ids, vals['branch_manager'])

                        return super(MembershipHandlersChild, self).write(vals)
            except:
                print("except except except except")
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

    def update_translation_main_office(self):
        current_lang = self.env.context.get('lang')
        self = self.with_context(lang='en_US')
        eng_name = self.name
        self.struc.name = eng_name
        self.struc_2.name = eng_name
        self = self.with_context(lang='am_ET')
        amh_name = self.name
        self.struc.name = amh_name
        self.struc_2.name = amh_name
        self = self.with_context(lang='current_lang')

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
        user = []
        user.append(wereda.wereda_id.branch_manager.id)
        user.append(wereda.wereda_id.parent_id.parent_manager.id)
        for line in wereda.wereda_id.parent_id.city_id.city_manager:
            user.append(line.id)
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
                'users': [(6, 0, user)],

            }
            val_3 = {
                'name': vals['name'],
                'parent_id_2': par_2.id,
                'main_office': wereda.id,
                'wereda': vals['wereda_id'],
                'is_member': True,
                'is_league': True,
                'is_supporter': True,
                'users': [(6, 0, user)],

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


class MembershipCityHandlers(models.Model):
    _inherit = "membership.city.handlers"

    def write(self, vals):
        try:
            if vals['city_manager']:
                before = set(self.city_manager.ids)
                after = set(vals['city_manager'][0][2])
                diff1 = after.difference(before)
                diff2 = before.difference(after)
                print("diff1", diff1)
                print("diff2", diff2)
                if diff2:
                    memb = self.env['membership.structure'].search([])
                    legues = self.env['league.structure'].search([])
                    suppo = self.env['supporter.structure'].search([])
                    for line in memb:
                        for id in diff2:
                            if id == line.sub_city.parent_manager.id or id == line.wereda.branch_manager.id:
                                print("ok")
                            else:
                                arr = []
                                for us in line.users:
                                    if id != us.id:
                                        arr.append(us.id)
                                # line.users = [(6,0,[])]
                                print("before", line.users)
                                line.users = [(6, 0, arr)]
                                print("after", line.users)
                    for line in legues:
                        for id in diff2:
                            if id == line.sub_city.parent_manager.id or id == line.wereda.branch_manager.id:
                                print("ok")
                            else:
                                arr = []
                                for us in line.users:
                                    if id != us.id:
                                        arr.append(us.id)
                                # line.users = [(6,0,[])]
                                line.users = [(6, 0, arr)]
                    for line in suppo:
                        for id in diff2:
                            if id == line.sub_city.parent_manager.id or id == line.wereda.branch_manager.id:
                                print("ok")
                            else:
                                arr = []
                                for us in line.users:
                                    if id != us.id:
                                        arr.append(us.id)
                                # line.users = [(6,0,[])]
                                line.users = [(6, 0, arr)]
                if diff1:
                    memb = self.env['membership.structure'].search([])
                    legues = self.env['league.structure'].search([])
                    suppo = self.env['supporter.structure'].search([])
                for id in diff1:
                    for line in memb:
                        new_arr = line.users.ids
                        print("new_arr", type(new_arr), id)
                        new_arr.append(id)
                        print("new_arr_2", new_arr)
                        line.users = [(6, 0, new_arr)]
                    for line in legues:
                        new_arr = line.users.ids
                        new_arr.append(id)
                        line.users = [(6, 0, new_arr)]
                    for line in suppo:
                        new_arr = line.users.ids
                        new_arr.append(id)
                        line.users = [(6, 0, new_arr)]
                return super(MembershipCityHandlers, self).write(vals)

        except:
            return super(MembershipCityHandlers, self).write(vals)
