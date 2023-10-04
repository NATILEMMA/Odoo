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

        sub_city = self.env['membership.handlers.parent'].sudo().search([])
        for sub in sub_city:
            par = self.env['membership.structure'].sudo().search([('name', '=', sub.name)])
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

        wereda = self.env['membership.handlers.branch'].sudo().search([])
        for wor in wereda:
            par_1 = self.env['membership.structure'].sudo().search(
                [('name', '=', wor.name), ('sub_city', '=', wor.parent_id.id)])
            if not par_1:
                par = self.env['membership.structure'].sudo().search([('name', '=', wor.parent_id.name)], limit=1)
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

        main_office = self.env['main.office'].sudo().search([])
        for main in main_office:
            par_2 = self.env['membership.structure'].sudo().search(
                [('name', '=', main.name), ('wereda', '=', main.wereda_id.id),
                 ('sub_city', '=', main.wereda_id.parent_id.id)])
            if not par_2:
                par = self.env['membership.structure'].sudo().search(
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
        cells = self.env['member.cells'].sudo().search([])
        for cell in cells:
            if cell.main_office:
                cell_main_office = cell.main_office

            par_2 = self.env['membership.structure'].sudo().search(
                [('name', '=', cell.name), ('main_office', '=', cell_main_office.id),
                 ('wereda', '=', cell.wereda_id.id), ('sub_city', '=', cell.wereda_id.parent_id.id)])
            if not par_2:
                par = self.env['membership.structure'].sudo().search(
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

            partner = self.env['res.partner'].sudo().search([])
            candidate = self.env['candidate.members'].sudo().search([])
            supporter = self.env['supporter.members'].sudo().search([])
            for part in partner:
                if part.member_cells:
                    par_2 = self.env['membership.structure'].sudo().search([('cell', '=', part.member_cells.id)])
                    for line_2 in par_2:
                        part.struc = line_2.id
                if part.wereda_id and not part.member_cells and not part.struc:
                    par_3 = self.env['membership.structure'].sudo().search(
                        [('wereda', '=', part.wereda_id.id), ('name', '=', part.wereda_id.name)])
                    for line in par_3:
                        part.struc = par_3.id
            for cand in candidate:
                if cand.wereda_id:
                    par_2 = self.env['membership.structure'].sudo().search(
                        [('wereda', '=', part.wereda_id.id), ('name', '=', part.wereda_id.name)])
                    cand.struc = par_2.id

            for supp in supporter:
                if supp.wereda_id:
                    par_2 = self.env['membership.structure'].sudo().search(
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
                woreda_ia = self.env['membership.handlers.branch'].sudo().search([('id', '=', vals['wereda_id'])])
                par = self.env['membership.structure'].sudo().search(
                    [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                par_2 = self.env['league.structure'].sudo().search(
                    [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                res.struc = par.id
                res.struc_2 = par_2.id
        except:
            return res
        return res

    def write(self, vals):
        try:
            print("vals in partner", vals['member_cells'])
            # if vals['member_cells']:
            print("if val")
            cell = self.env['membership.structure'].sudo().search([('cell', '=', vals['member_cells'])])
            cell_2 = self.env['league.structure'].sudo().search([('cell', '=', vals['member_cells'])])
            self.struc = cell.id
            self.struc_2 = cell_2.id
            print("self.struc", self.struc, "self.struc_2", self.struc)
        except:
            try:
                if vals['wereda_id']:
                    woreda_ia = self.env['membership.handlers.branch'].sudo().search([('id', '=', vals['wereda_id'])])
                    print("woreda_ia", woreda_ia.id, woreda_ia.name)
                    par = self.env['membership.structure'].sudo().search(
                        [('wereda', '=', woreda_ia.id), ('name', '=', woreda_ia.name)])
                    par_2 = self.env['league.structure'].sudo().search(
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
        for rec in self:
            current_lang = self.env.context.get('lang')
            rec = rec.with_context(lang='en_US')
            eng_name = rec.name_2
            rec.struc.name = eng_name
            rec.struc_2.name = eng_name
            rec= rec.with_context(lang='am_ET')
            amh_name = rec.name_2
            rec.struc.name = amh_name
            rec.struc_2.name = amh_name
            rec = rec.with_context(lang='current_lang')

    @api.model
    def create(self, vals):
        wereda = super(Cells, self).create(vals)
        if vals['for_which_members'] == 'member':
            sub = self.env['main.office'].sudo().search([('id', '=', wereda.main_office.id)], limit=1)
            sub_2 = False
        else:
            sub_2 = self.env['main.office'].sudo().search([('id', '=', wereda.main_office.id)], limit=1)
            sub = False
        if sub:
            par_1 = self.env['membership.structure'].sudo().search(
                [('name', '=', wereda.name_2), ('main_office', '=', sub.id)])
        if sub_2:
            par_1 = self.env['membership.structure'].sudo().search(
                [('name', '=', wereda.name_2), ('main_office', '=', sub_2.id)])
        user = self.env.user
        config = self.env['cell.configuration'].sudo().search(
            [('for_members_or_leagues', '=', wereda.for_which_members)])
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
            if wereda.wereda_id.branch_manager.ids:
                for line in wereda.wereda_id.branch_manager.ids:
                    user.append(line)
            if wereda.wereda_id.ict_manager.id:
                user.append(wereda.wereda_id.ict_manager.id)
            if wereda.wereda_id.parent_id.parent_manager.ids:
                for line in wereda.wereda_id.parent_id.parent_manager.ids:
                    user.append(line)
            if wereda.wereda_id.parent_id.ict_manager.id:
                user.append(wereda.wereda_id.parent_id.ict_manager.id)
            for line in wereda.main_office.wereda_id.parent_id.city_id.city_manager:
                user.append(line.id)
            res = self.env['responsible.bodies'].sudo().search([])
            for name in res:
                for line in name.system_admin:
                    user.append(line.id)
            mo = wereda.main_office
            print('mo', mo)

        else:
            user = []
            if wereda.wereda_id.branch_manager.ids:
                for line in wereda.wereda_id.branch_manager.ids:
                    user.append(line)
            if wereda.wereda_id.ict_manager.id:
                user.append(wereda.wereda_id.ict_manager.id)
            if wereda.wereda_id.parent_id.parent_manager.ids:
                for line in wereda.wereda_id.parent_id.parent_manager.ids:
                    user.append(line)
            if wereda.wereda_id.parent_id.ict_manager.id:
                user.append(wereda.wereda_id.parent_id.ict_manager.id)
            for line in wereda.main_office.wereda_id.parent_id.city_id.city_manager:
                user.append(line.id)
            res = self.env['responsible.bodies'].sudo().search([])
            for name in res:
                for line in name.system_admin:
                    user.append(line.id)
            mo = wereda.main_office
        if not par_1:
            if sub:
                par = self.env['membership.structure'].sudo().search(
                    [('main_office', '=', sub.id), ('name', '=', sub.struc.name)], limit=1)
                if not par:
                    par = self.env['league.structure'].sudo().search(
                    [('main_office', '=', sub.id), ('name', '=', sub.struc_2.name)], limit=1)
                val = {
                    'name': wereda.name_2,
                    'parent_id_2': par.id,
                    'main_office': mo.id,
                    'sub_city': vals['subcity_id'],
                    'cell': wereda.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,
                    'users': [(6, 0, user)],

                }
            if sub_2:
                par_2 = self.env['league.structure'].sudo().search(
                    [('main_office', '=', sub_2.id), ('name', '=', sub_2.struc_2.name)], limit=1)
                val_3 = {
                    'name': wereda.name_2,
                    'parent_id_2': par_2.id,
                    'main_office': mo.id,
                    'sub_city': vals['subcity_id'],
                    'cell': wereda.id,
                    'is_member': True,
                    'is_league': True,
                    'is_supporter': True,
                    'users': [(6, 0, user)],

                }

            if wereda.for_which_members == 'member':
                if not wereda.struc:
                    res = self.env['membership.structure'].sudo().create(val)
                    res.name = wereda.name_2
                    for line in wereda.members_ids:
                        line.struc = res.id
                    wereda.struc = res.id

            else:
                if not wereda.struc_2:
                    res_3 = self.env['league.structure'].sudo().create(val_3)
                    res_3.name = wereda.name_2
                    for line in wereda.members_ids:
                        line.struc = res_3.id
                    wereda.struc_2 = res_3.id

        return wereda

    def write(self, vals):
        try:
            old_set = set(vals['members_ids'][0][2])
            new_set = set(self.members_ids.ids)
            removed_elements = new_set - old_set
            records = self.env['res.partner'].search([('id', 'in', list(removed_elements))])
            for i in records:
                i.member_cells = False
                i.struc = i.wereda_id.struc.id
                i.struc_2 = i.wereda_id.struc_2.id
        except:
            pass
        try:
            if vals['name_2']:
                self.struc.write({'name': vals['name_2']})
                self.struc_2.write({'name': vals['name_2']})
        except:
            pass
        try:
            if vals['woreda_id']:
                sun = self.env['main.office'].sudo().search([('id', '=', vals['main_office'])])
                par = self.env['membership.structure'].sudo().search([('name', '=', sun.name)])
                par_2 = self.env['league.structure'].sudo().search([('name', '=', sun.name)])
                self.struc.write({'parent_id_2': par})
                self.struc_2.write({'parent_id_2': par_2})
        except:
            pass
        res = super(Cells, self).write(vals)
        if vals.get("main_office"):
            sub = self.env['main.office'].sudo().search([('id', '=', vals['main_office'])], limit=1)
            if sub.struc.id:
                self.struc.parent_id_2 = sub.struc.id
                self.struc.main_office = sub.id
                self.struc.sub_city = sub.subcity_id.id
                self.struc.wereda = sub.wereda_id.id
            if sub.struc_2.id:
                self.struc_2.parent_id_2 = sub.struc_2.id
                self.struc.main_office = sub.id
                self.struc.sub_city = sub.subcity_id.id
                self.struc.wereda = sub.wereda_id.id
        return res

    def unlink(self):
        for rec in self:
            if rec.for_which_members == 'member':
                if rec.struc:
                    par = self.env['membership.structure'].sudo().search([('id', '=', rec.struc.id)])
                    par.unlink()
                else:
                    if rec.struc_2:
                        par = self.env['league.structure'].sudo().search([('id', '=', rec.struc_2.id)])
                        par.unlink() 
            else:
                if rec.struc_2:
                        par = self.env['league.structure'].sudo().search([('id', '=', rec.struc_2.id)])
                        par.unlink()
        return super(Cells, self).unlink()


class MembershipHandlersParent(models.Model):
    _inherit = 'membership.handlers.parent'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_3 = fields.Many2one('supporter.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('league.structure', string="Structure", store=True)

    def update_translation_parent(self):
        for line in self:
            current_lang = line.env.context.get('lang')
            line = line.with_context(lang='en_US')
            eng_name = line.name
            line.struc.name = eng_name
            line.struc_2.name = eng_name
            line.struc_3.name = eng_name
            line = line.with_context(lang='am_ET')
            amh_name = line.name
            line.struc.name = amh_name
            line = self.with_context(lang='current_lang')
            print("translation", amh_name, eng_name)
        return

    @api.model
    def create(self, vals):
        test = self.env['membership.handlers.parent'].sudo().search([('name', '=', vals['name'])])
        res = self.env['responsible.bodies'].sudo().search([])
        if test:
            raise UserError(_("Please change your Subcity name there a name duplication."))
        par_1 = self.env['membership.structure'].sudo().search([('name', '=', vals['name'])])
        wereda = super(MembershipHandlersParent, self).create(vals)
        user = []
        user.append(wereda.ict_manager.id)
        for line in wereda.parent_manager:
            user.append(line.id)
        if res:
            for line in res.system_admin:
                user.append(line.id)
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
        if vals.get("name"):
            self.struc.write({'name': vals['name']})
            self.struc_2.write({'name': vals['name']})
            self.struc_3.write({'name': vals['name']})
        if vals.get("parent_manager"):
          if vals['parent_manager'][0] != (5, 0, 0):  
            parent_manager = []
            for line in self.parent_manager:
                parent_manager.append(line.id)
            set_a = set(parent_manager)
            set_b = set(vals['parent_manager'][0][2])
            difference = set_a - set_b
            par = self.env['membership.structure'].sudo().search([('sub_city', '=', self.id)])
            par_2 = self.env['league.structure'].sudo().search([('sub_city', '=', self.id)])
            par_3 = self.env['supporter.structure'].sudo().search([('sub_city', '=', self.id)])
            for str in par:
                user = []
                for man in vals['parent_manager'][0][2]:
                    user.append(man)
                for id in str.users:
                    if id.id not in list(difference):
                        user.append(id.id)
                print(user)
                str.users = [(6, 0, user)]
            for str in par_2:
                user = []
                for man in vals['parent_manager'][0][2]:
                    user.append(man)
                for id in str.users:
                    if id.id not in list(difference):
                        user.append(id.id)
                str.users = [(6, 0, user)]
            for str in par_3:
                user = []
                for man in vals['parent_manager'][0][2]:
                    user.append(man)
                for id in str.users:
                    if id.id not in list(difference):
                        user.append(id.id)
                str.users = [(6, 0, user)]
        if vals.get("ict_manager"):
            par = self.env['membership.structure'].sudo().search([('sub_city', '=', self.id)])
            par_2 = self.env['league.structure'].sudo().search([('sub_city', '=', self.id)])
            par_3 = self.env['supporter.structure'].sudo().search([('sub_city', '=', self.id)])
            for str in par:
                user = []
                user.append(vals['ict_manager'])
                for id in str.users:
                    if id.id != self.ict_manager.id:
                        user.append(id.id)
                print(user)
                str.users = [(6, 0, user)]
            for str in par_2:
                user = []
                user.append(vals['ict_manager'])
                for id in str.users:
                    if id.id != self.ict_manager.id:
                        user.append(id.id)
                str.users = [(6, 0, user)]
            for str in par_3:
                user = []
                user.append(vals['ict_manager'])
                for id in str.users:
                    if id.id != self.ict_manager.id:
                        user.append(id.id)
                str.users = [(6, 0, user)]
        return super(MembershipHandlersParent, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.struc:
                par = self.env['membership.structure'].sudo().search([('id', '=', rec.struc.id)])
                par.unlink()
            if rec.struc_2:
                if rec.struc_2:
                    par = self.env['league.structure'].sudo().search([('id', '=', rec.struc_2.id)])
                    par.unlink()
            if rec.struc_3:
                if rec.struc_3:
                    par = rec.env['supporter.structure'].sudo().search([('id', '=', rec.struc_3.id)])
                    par.unlink()
        return super(MembershipHandlersParent, self).unlink()


class MembershipHandlersChild(models.Model):
    _inherit = 'membership.handlers.branch'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_3 = fields.Many2one('supporter.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('league.structure', string="Structure", store=True)

    def update_translation_branch(self):
        for line in self:
            current_lang = line.env.context.get('lang')
            line = line.with_context(lang='en_US')
            eng_name = line.name
            line.struc.name = eng_name
            line = line.with_context(lang='am_ET')
            amh_name = line.name
            line.struc.name = amh_name
            line = line.with_context(lang='current_lang')

    @api.model
    def create(self, vals):
        test = self.env['membership.handlers.branch'].sudo().search([('name', '=', vals['name'])])
        if test:
            raise UserError(_("Please change your Wereda name there a name duplication"))
        name = self.env['membership.handlers.parent'].sudo().search([('name', '=', vals['name'])], limit=1)
        if name:
            raise UserError(_("There is subcity called " + str(vals['name'])))
        sub = self.env['membership.handlers.parent'].sudo().search([('id', '=', vals['parent_id'])], limit=1)
        par_1 = self.env['membership.structure'].sudo().search([('name', '=', vals['name']), ('sub_city', '=', sub.id)])
        wereda = super(MembershipHandlersChild, self).create(vals)
        user = []
        res = self.env['responsible.bodies'].sudo().search([])
        for name in res:
            for line in name.system_admin:
                user.append(line.id)
        for line in wereda.branch_manager.ids:
            user.append(line)
        user.append(wereda.ict_manager.id)
        user.append(wereda.parent_id.ict_manager.id)
        for line in wereda.parent_id.parent_manager.ids:
            user.append(line)
        for line in wereda.parent_id.city_id.city_manager:
            user.append(line.id)
        if not par_1:
            par = self.env['membership.structure'].sudo().search([('name', '=', sub.name)], limit=1)
            par_3 = self.env['supporter.structure'].sudo().search([('name', '=', sub.name)], limit=1)
            par_2 = self.env['league.structure'].sudo().search([('name', '=', sub.name)], limit=1)
            arr = par.users.ids
            for line in wereda.branch_manager.ids:
                arr.append(line)
            arr.append(wereda.ict_manager.id)
            print("arr", arr)
            par.users = [(6, 0, arr)]
            par_2.users = [(6, 0, arr)]
            par_3.users = [(6, 0, arr)]
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
        if vals.get("parent_id"):
            sun = self.env['membership.handlers.parent'].sudo().search([('id', '=', vals['parent_id'])])
            par = self.env['membership.structure'].sudo().search([('name', '=', sun.name)])
            par_2 = self.env['supporter.structure'].sudo().search([('name', '=', sun.name)])
            par_3 = self.env['league.structure'].sudo().search([('name', '=', sun.name)])
            self.struc.write({'parent_id_2': par})
            self.struc_2.write({'parent_id_2': par_2})
            self.struc_3.write({'parent_id_2': par_3})
        if vals.get("name"):
            self.struc.write({'name': vals['name']})
            self.struc_2.write({'name': vals['name']})
            self.struc_3.write({'name': vals['name']})
        if vals.get("ict_manager"):
            arr = self.struc.sub_city.struc.users.ids
            arr.append(vals['ict_manager'])
            self.struc.sub_city.struc.users = [(6, 0, arr)]
            self.struc.sub_city.struc.users = [(6, 0, arr)]
            self.struc.sub_city.struc.users = [(6, 0, arr)]
            par = self.env['membership.structure'].sudo().search([('wereda', '=', self.id)])
            par_2 = self.env['supporter.structure'].sudo().search([('wereda', '=', self.id)])
            par_3 = self.env['league.structure'].sudo().search([('wereda', '=', self.id)])
            for str in par:
                user = []
                user.append(vals['ict_manager'])
                for id in str.users:
                    print("od", id.id, self.ict_manager)
                    if id.id not in self.branch_manager.ids and id.id != self.ict_manager.id:
                        user.append(id.id)
                str.users = [(6, 0, user)]
            for str in par_2:
                user = []
                user.append(vals['ict_manager'])
                for id in str.users:
                    if id.id not in self.branch_manager.ids and id.id != self.ict_manager.id:
                        user.append(id.id)
                str.users = [(6, 0, user)]
            for str in par_3:
                user = []
                user.append(vals['ict_manager'])
                for id in str.users:
                    if id.id not in self.branch_manager.ids and id.id != self.ict_manager.id:
                        user.append(id.id)
                str.users = [(6, 0, user)]
            if self.ict_manager.id not in self.branch_manager.ids:
                if self.ict_manager.id not in self.parent_id.city_id.city_manager.ids:
                    arr = []
                    arr_2 = []
                    arr_3 = []
                    arr.append(vals[''])
                    arr_2.append(vals['ict_manager'])
                    arr_3.append(vals['ict_manager'])
                    for usr in self.parent_id.struc.users.ids:
                        if usr not in self.branch_manager.ids and usr != self.ict_manager.id:
                            arr.append(usr)
                    for usr in self.parent_id.struc_2.users.ids:
                        if usr not in self.branch_manager.ids and usr != self.ict_manager.id:
                            arr_2.append(usr)
                    for usr in self.parent_id.struc_3.users.ids:
                        if usr not in self.branch_manager.ids and usr != self.ict_manager.id:
                            arr_3.append(usr)
                    self.parent_id.struc.users = [(6, 0, arr)]
                    self.parent_id.struc_2.users = [(6, 0, arr_2)]
                    self.parent_id.struc_3.users = [(6, 0, arr_3)]
        if vals.get("branch_manager"):
            branch_manager = []
            for br in self.branch_manager.ids:
                branch_manager.append(br)
            set_a = set(branch_manager)
            set_b = set(vals['branch_manager'][0][2])
            difference = set_a - set_b
            arr = self.struc.sub_city.struc.users.ids
            for line in vals['branch_manager'][0][2]:
                arr.append(line)
            print("arr", arr)
            self.struc.sub_city.struc.users = [(6, 0, arr)]
            self.struc.sub_city.struc.users = [(6, 0, arr)]
            self.struc.sub_city.struc.users = [(6, 0, arr)]
            par = self.env['membership.structure'].sudo().search([('wereda', '=', self.id)])
            par_2 = self.env['supporter.structure'].sudo().search([('wereda', '=', self.id)])
            par_3 = self.env['league.structure'].sudo().search([('wereda', '=', self.id)])
            for str in par:
                user = []
                for line in vals['branch_manager'][0][2]:
                    user.append(line)
                for id in str.users:
                    if id.id not in difference:
                        user.append(id.id)
                str.users = [(6, 0, user)]
            for str in par_2:
                user = []
                for line in vals['branch_manager'][0][2]:
                    user.append(line)
                for id in str.users:
                    if id.id not in difference:
                        user.append(id.id)
                str.users = [(6, 0, user)]
            for str in par_3:
                user = []
                for line in vals['branch_manager'][0][2]:
                    user.append(line)
                for id in str.users:
                    if id.id not in difference:
                        user.append(id.id)
                str.users = [(6, 0, user)]
            if difference not in self.parent_id.city_id.city_manager.ids:
                arr = []
                arr_2 = []
                arr_3 = []
                for line in vals['branch_manager'][0][2]:
                    arr.append(line)
                    arr_2.append(line)
                    arr_3.append(line)
                for usr in self.parent_id.struc.users.ids:
                    print("usr", usr)
                    print("difference", difference)
                    if usr not in difference:
                        print("True")
                        arr.append(usr)
                for usr in self.parent_id.struc_2.users.ids:
                    if usr not in difference:
                        arr_2.append(usr)
                for usr in self.parent_id.struc_3.users.ids:
                    if usr not in difference:
                        arr_3.append(usr)
                self.parent_id.struc.users = [(6, 0, arr)]
                self.parent_id.struc_2.users = [(6, 0, arr_2)]
                self.parent_id.struc_3.users = [(6, 0, arr_3)]
        return super(MembershipHandlersChild, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.struc:
                par = self.env['membership.structure'].sudo().search([('id', '=', rec.struc.id)])
                par.unlink()
            if rec.struc_2:
                if rec.struc_2:
                    par = rec.env['league.structure'].sudo().search([('id', '=', rec.struc_2.id)])
                    par.unlink()
            if rec.struc_3:
                if rec.struc_3:
                    par = rec.env['supporter.structure'].sudo().search([('id', '=', rec.struc_3.id)])
                    par.unlink()
        return super(MembershipHandlersChild, rec).unlink()


class MainOffice(models.Model):
    _inherit = 'main.office'

    struc = fields.Many2one('membership.structure', string="Structure", store=True)
    struc_2 = fields.Many2one('league.structure', string="Structure", store=True)

    def update_translation_main_office(self):
         for rec in self:
            if rec.for_which_members == 'member':
                if rec.for_which_members == 'member':
                    if rec.duplicate:
                        if rec.main_office_id.league_type == 'young':
                            rec.struc.with_context(lang='en_US').name = rec.member_main_type_id.with_context(
                                lang='en_US').name + '/Youngster/' + rec.with_context(lang='en_US').name_2
                            rec.struc.with_context(lang='am_ET').name = rec.member_main_type_id.with_context(
                                lang='am_ET').name + '/ወጣት ሊግ/' + rec.with_context(lang='am_ET').name_2
                        else:
                            rec.struc.name = rec.member_main_type_id.with_context(
                                lang='en_US').name + '/Woman/' + rec.with_context(lang='en_US').name_2
                            rec.struc.with_context(lang='am_ET').name = rec.with_context(
                                lang='am_ET').member_main_type_id.name + '/ሴት ሊግ/' + rec.with_context(lang='am_ET').name_2
                    else:
                        rec.struc.with_context(lang='en_US').name = rec.member_main_type_id.with_context(
                            lang='en_US').name + '/Member/' + rec.with_context(lang='en_US').name_2
                        rec.struc.with_context(lang='am_ET').name = rec.member_main_type_id.with_context(
                            lang='am_ET').name + '/አባል/' + rec.with_context(lang='am_ET').name_2
            else:
                if not rec.struc_2:
                    if rec.for_which_members == 'league' and rec.league_type == 'young':
                        rec.struc_2.with_context(lang='en_US').name = rec.member_main_type_id.with_context(
                            lang='en_US').name + '/Youngster/' + rec.with_context(lang='en_US').name_2
                        rec.struc_2.with_context(lang='am_ET').name = rec.member_main_type_id.with_context(
                            lang='am_ET').name + '/ወጣት ሊግ/' + rec.with_context(lang='am_ET').name_2
                    if rec.for_which_members == 'league' and rec.league_type == 'women':
                        rec.struc_2.with_context(lang='en_US').name = rec.member_main_type_id.with_context(
                            lang='en_US').name + '/Woman/' + rec.with_context(lang='en_US').name_2
                        rec.struc_2.with_context(lang='am_ET').name = rec.member_main_type_id.with_context(
                            lang='am_ET').name + '/ሴት ሊግ/' + rec.with_context(lang='am_ET').name_2

    def unlink(self):
        for rec in self:
            if rec.struc:
                par = self.env['membership.structure'].sudo().search([('id', '=', rec.struc.id)])
                par.unlink()
            else:
                if rec.struc_2:
                    par = self.env['league.structure'].sudo().search([('id', '=', rec.struc_2.id)])
                    par.unlink()
        return super(MainOffice, self).unlink()

    @api.model
    def create(self, vals):
        print("str create", vals)
        sub = self.env['membership.handlers.branch'].sudo().search([('id', '=', vals['wereda_id'])], limit=1)
        wereda = super(MainOffice, self).create(vals)
        par_1 = self.env['membership.structure'].sudo().search([('name', '=', wereda.name), ('wereda', '=', sub.id)])
        print("worda", sub.id, vals['wereda_id'])
        user = []
        res = self.env['responsible.bodies'].sudo().search([])
        for name in res:
            for line in name.system_admin:
                user.append(line.id)
        for line in wereda.wereda_id.branch_manager.ids:
            user.append(line)
        user.append(wereda.wereda_id.ict_manager.id)
        user.append(wereda.wereda_id.parent_id.ict_manager.id)
        for line in wereda.wereda_id.parent_id.parent_manager.ids:
            user.append(line)
        for line in wereda.wereda_id.parent_id.city_id.city_manager:
            user.append(line.id)
        if not par_1:
            par = self.env['membership.structure'].sudo().search([('name', '=', sub.name)], limit=1)
            par_3 = self.env['supporter.structure'].sudo().search([('name', '=', sub.name)], limit=1)
            par_2 = self.env['league.structure'].sudo().search([('name', '=', sub.name)], limit=1)
            arr = par.users.ids
            for line in wereda.wereda_id.branch_manager.ids:
                arr.append(line)
            arr.append(wereda.wereda_id.ict_manager.id)
            print("arr", arr)
            par.users = [(6, 0, arr)]
            par_2.users = [(6, 0, arr)]
            par_3.users = [(6, 0, arr)]
        if not par_1:
            par = self.env['membership.structure'].sudo().search([('name', '=', sub.name)], limit=1)
            par_2 = self.env['league.structure'].sudo().search([('name', '=', sub.name)], limit=1)
            val = {
                'name': wereda.name,
                'parent_id_2': par.id,
                'wereda': vals['wereda_id'],
                'sub_city': vals['subcity_id'],
                'main_office': wereda.id,
                'is_member': True,
                'is_league': True,
                'is_supporter': True,
                'users': [(6, 0, user)],

            }
            val_3 = {
                'name': wereda.name,
                'parent_id_2': par_2.id,
                'main_office': wereda.id,
                'wereda': vals['wereda_id'],
                'sub_city': vals['subcity_id'],
                'is_member': True,
                'is_league': True,
                'is_supporter': True,
                'users': [(6, 0, user)],

            }
            if vals['for_which_members'] == 'member':
                res = self.env['membership.structure'].sudo().create(val)
                if wereda.for_which_members == 'member':
                    if wereda.duplicate:
                        if wereda.main_office_id.league_type == 'young':
                            res.with_context(lang='en_US').name = wereda.member_main_type_id.with_context(
                                lang='en_US').name + '/Youngster/' + wereda.name_2
                            res.with_context(lang='am_ET').name = wereda.member_main_type_id.with_context(
                                lang='am_ET').name + '/ወጣት ሊግ/' + wereda.name_2
                        else:
                            res.name = wereda.member_main_type_id.with_context(
                                lang='en_US').name + '/Woman/' + wereda.name_2
                            res.with_context(lang='am_ET').name = wereda.with_context(
                                lang='am_ET').member_main_type_id.name + '/ሴት ሊግ/' + wereda.name_2
                    else:
                        res.with_context(lang='en_US').name = wereda.member_main_type_id.with_context(
                            lang='en_US').name + '/Member/' + wereda.name_2
                        res.with_context(lang='am_ET').name = wereda.member_main_type_id.with_context(
                            lang='am_ET').name + '/አባል/' + wereda.name_2
                wereda.struc = res.id
            else:
                if not wereda.struc_2:
                    res = self.env['league.structure'].sudo().create(val_3)
                    if wereda.for_which_members == 'league' and wereda.league_type == 'young':
                        res.with_context(lang='en_US').name = wereda.member_main_type_id.with_context(
                            lang='en_US').name + '/Youngster/' + wereda.name_2
                        res.with_context(lang='am_ET').name = wereda.member_main_type_id.with_context(
                            lang='am_ET').name + '/ወጣት ሊግ/' + wereda.name_2
                    if wereda.for_which_members == 'league' and wereda.league_type == 'women':
                        res.with_context(lang='en_US').name = wereda.member_main_type_id.with_context(
                            lang='en_US').name + '/Woman/' + wereda.name_2
                        res.with_context(lang='am_ET').name = wereda.member_main_type_id.with_context(
                            lang='am_ET').name + '/ሴት ሊግ/' + wereda.name_2
                    wereda.struc_2 = res.id

        return wereda

    def write(self, vals):
        if vals.get("name_2"):
            if self.for_which_members == 'member':
                if self.for_which_members == 'member':
                    if self.duplicate:
                        if self.main_office_id.league_type == 'young':
                            self.struc.with_context(lang='en_US').name = self.member_main_type_id.with_context(
                                lang='en_US').name + '/Youngster/' + vals['name_2']
                            self.struc.with_context(lang='am_ET').name = self.member_main_type_id.with_context(
                                lang='am_ET').name + '/ወጣት ሊግ/' + vals['name_2']
                        else:
                            self.struc.name = self.member_main_type_id.with_context(
                                lang='en_US').name + '/Woman/' + vals['name_2']
                            self.struc.with_context(lang='am_ET').name = self.with_context(
                                lang='am_ET').member_main_type_id.name + '/ሴት ሊግ/' + vals['name_2']
                    else:
                        self.struc.with_context(lang='en_US').name = self.member_main_type_id.with_context(
                            lang='en_US').name + '/Member/' + vals['name_2']
                        self.struc.with_context(lang='am_ET').name = self.member_main_type_id.with_context(
                            lang='am_ET').name + '/አባል/' + vals['name_2']
            else:
                if not self.struc_2:
                    if self.for_which_members == 'league' and self.league_type == 'young':
                        self.struc_2.with_context(lang='en_US').name = self.member_main_type_id.with_context(
                            lang='en_US').name + '/Youngster/' + vals['name_2']
                        self.struc_2.with_context(lang='am_ET').name = self.member_main_type_id.with_context(
                            lang='am_ET').name + '/ወጣት ሊግ/' + vals['name_2']
                    if self.for_which_members == 'league' and self.league_type == 'women':
                        self.struc_2.with_context(lang='en_US').name = self.member_main_type_id.with_context(
                            lang='en_US').name + '/Woman/' + vals['name_2']
                        self.struc_2.with_context(lang='am_ET').name = self.member_main_type_id.with_context(
                            lang='am_ET').name + '/ሴት ሊግ/' + vals['name_2']
        if vals.get("member_main_type_id"):
            org = self.env['membership.organization'].sudo().search([('id', '=', vals['member_main_type_id'])])
            if self.for_which_members == 'member':
                if self.for_which_members == 'member':
                    if self.duplicate:
                        if self.main_office_id.league_type == 'young':
                            self.struc.with_context(lang='en_US').name = org.with_context(
                            lang='en_US').name + '/Youngster/' + self.name_2
                            self.struc.with_context(lang='am_ET').name = org.with_context(
                            lang='en_US').name + '/ወጣት ሊግ/' + self.name_2
                        else:
                            self.struc.name = org.with_context(
                                lang='en_US').name + '/Woman/' + self.name_2
                            self.struc.with_context(lang='am_ET').name = org.with_context(
                                lang='am_ET').member_main_type_id.name + '/ሴት ሊግ/' + self.name_2
                    else:
                        self.struc.with_context(lang='en_US').name = org.with_context(
                            lang='en_US').name + '/Member/' + self.name_2
                        self.struc.with_context(lang='am_ET').name = org.with_context(
                            lang='am_ET').name + '/አባል/' + self.name_2
            else:
                if not self.struc_2:
                    if self.for_which_members == 'league' and self.league_type == 'young':
                        self.struc_2.with_context(lang='en_US').name = org.with_context(
                            lang='en_US').name + '/Youngster/' + self.name_2
                        self.struc_2.with_context(lang='am_ET').name = org.with_context(
                            lang='am_ET').name + '/ወጣት ሊግ/' + self.name_2
                    if self.for_which_members == 'league' and self.league_type == 'women':
                        self.struc_2.with_context(lang='en_US').name = org.with_context(
                            lang='en_US').name + '/Woman/' + self.name_2
                        self.struc_2.with_context(lang='am_ET').name = org.with_context(
                            lang='am_ET').name + '/ሴት ሊግ/' + self.name_2
        if vals.get("woreda_id"):
            sun = self.env['membership.handlers.branch'].sudo().search([('id', '=', vals['woreda_id'])])
            par = self.env['membership.structure'].sudo().search([('name', '=', sun.name)])
            par_2 = self.env['league.structure'].sudo().search([('name', '=', sun.name)])
            if self.struc:
                self.struc.write({'parent_id_2': par})
            if self.struc_2:
                self.struc_2.write({'parent_id_2': par_2})
            if vals.get("for_which_members"):
                if vals['for_which_members'] == 'member':
                    sun = self.env['membership.handlers.branch'].sudo().search([('id', '=', vals['wereda_id'])])
                    par = self.env['membership.structure'].sudo().search([('name', '=', sun.name)])
                    self.struc.write({'parent_id_2': par})
                else:
                    sun = self.env['membership.handlers.branch'].sudo().search([('id', '=', vals['wereda_id'])])
                    par = self.env['league.structure'].sudo().search([('name', '=', sun.name)])
                    self.struc.write({'parent_id_2': par})
        #
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
                if diff2:
                    memb = self.env['membership.structure'].sudo().search([])
                    legues = self.env['league.structure'].sudo().search([])
                    suppo = self.env['supporter.structure'].sudo().search([])
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
                    memb = self.env['membership.structure'].sudo().search([])
                    legues = self.env['league.structure'].sudo().search([])
                    suppo = self.env['supporter.structure'].sudo().search([])
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


class ResponsibleBodies(models.Model):
    _inherit = "responsible.bodies"

    def write(self, vals):
        if vals['system_admin']:
            before = set(self.system_admin.ids)
            after = set(vals['system_admin'][0][2])
            diff1 = after.difference(before)
            diff2 = before.difference(after)
            if diff2:
                memb = self.env['membership.structure'].sudo().search([])
                legues = self.env['league.structure'].sudo().search([])
                suppo = self.env['supporter.structure'].sudo().search([])
                for line in memb:
                    for id in diff2:
                        if id in line.sub_city.parent_manager.ids or id in line.wereda.branch_manager.ids:
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
                        if id in line.sub_city.parent_manager.ids or id in line.wereda.branch_manager.ids:
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
                        if id in line.sub_city.parent_manager.ids or id in line.wereda.branch_manager.ids:
                            print("ok")
                        else:
                            arr = []
                            for us in line.users:
                                if id != us.id:
                                    arr.append(us.id)
                            # line.users = [(6,0,[])]
                            line.users = [(6, 0, arr)]
            if diff1:
                memb = self.env['membership.structure'].sudo().search([])
                legues = self.env['league.structure'].sudo().search([])
                suppo = self.env['supporter.structure'].sudo().search([])
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

        return super(ResponsibleBodies, self).write(vals)
