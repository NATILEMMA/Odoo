# Copyright 2014 ABF OSIELL <http://osiell.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import datetime
import logging

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class ResUsersRole(models.Model):
    _name = "res.users.role"
    _inherits = {"res.groups": "group_id"}
    _description = "User role"

    group_id = fields.Many2one(
        comodel_name="res.groups",
        required=True,
        ondelete="cascade",
        readonly=True,
        string="Associated group",
    )
    line_ids = fields.One2many(
        comodel_name="res.users.role.line", inverse_name="role_id", string="Role lines"
    )
    user_ids = fields.One2many(
        comodel_name="res.users", string="Users list", compute="_compute_user_ids"
    )
    group_category_id = fields.Many2one(
        related="group_id.category_id",
        default=lambda cls: cls.env.ref("base_user_role.ir_module_category_role").id,
        string="Associated category",
        help="Associated group's category",
        readonly=False,
    )
    comment = fields.Html(string="Internal Notes",)
    is_general = fields.Boolean(default=False)


    @api.onchange('implied_ids')
    def _prevent_duplication(self):
        """This function will check if there is duplication"""
        for record in self:
            if record.implied_ids:
                print(record.implied_ids)
                role_city = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_city_admin').id])])
                role_subcity = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_admin').id])])
                role_woreda = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_manager').id])])
                role_basic_manager = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_main_manager').id])])
                role_basic_assembler = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_main_assembler').id])])
                role_basic_finance = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_main_finance').id])])
                role_cell_admin = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_cell_manager').id])])
                role_cell_assembler = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_assembler').id])])
                role_cell_finance = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('member_minor_configuration.member_group_finance').id])])
                role_portal = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('base.group_portal').id])])
                role_internal = self.env['res.users.role'].search([('implied_ids', 'in', [self.env.ref('base.group_user').id])])
                if self.env.ref('member_minor_configuration.member_group_city_admin').id in record.implied_ids._origin.ids and role_city:
                    raise UserError(_("Member City Administrator has a Role in %s") % (role_city.name))
                if self.env.ref('member_minor_configuration.member_group_admin').id in record.implied_ids._origin.ids and role_subcity:
                    raise UserError(_("Member Sub City Administrator has a Role in %s") % (role_subcity.name))
                if self.env.ref('member_minor_configuration.member_group_manager').id in record.implied_ids._origin.ids and role_woreda:
                    raise UserError(_("Member Woreda Administrator has a Role in %s") % (role_woreda.name))

                if self.env.ref('member_minor_configuration.member_group_main_manager').id in record.implied_ids._origin.ids and role_basic_manager:
                    raise UserError(_("Member Basic Organization Administrator has a Role in %s") % (role_basic_manager.name))
                if self.env.ref('member_minor_configuration.member_group_main_assembler').id in record.implied_ids._origin.ids and role_basic_assembler:
                    raise UserError(_("Member Basic Organization Assembler has a Role in %s") % (role_basic_assembler.name))
                if self.env.ref('member_minor_configuration.member_group_main_finance').id in record.implied_ids._origin.ids and role_basic_finance:
                    raise UserError(_("Member Basic Organization Finance has a Role in %s") % (role_basic_finance.name))

                if self.env.ref('member_minor_configuration.member_group_cell_manager').id in record.implied_ids._origin.ids and role_cell_admin:
                    raise UserError(_("Member Cell Administrator has a Role in %s") % (role_cell_admin.name))
                if self.env.ref('member_minor_configuration.member_group_assembler').id in record.implied_ids._origin.ids and role_cell_assembler:
                    raise UserError(_("Member Cell Assembler has a Role in %s") % (role_cell_assembler.name))
                if self.env.ref('member_minor_configuration.member_group_finance').id in record.implied_ids._origin.ids and role_cell_finance:
                    raise UserError(_("Member Cell Finance has a Role in %s") % (role_cell_finance.name))

                if self.env.ref('base.group_portal').id in record.implied_ids._origin.ids and role_portal:
                    raise UserError(_("Portal User has a Role in %s") % (role_portal.name))
                if self.env.ref('base.group_user').id in record.implied_ids._origin.ids and role_internal:
                    raise UserError(_("Internal User has a Role in %s") % (role_internal.name))

    @api.depends("line_ids.user_id")
    def _compute_user_ids(self):
        for role in self:
            role.user_ids = role.line_ids.mapped("user_id")

    @api.model
    def create(self, vals):
        new_record = super(ResUsersRole, self).create(vals)
        new_record.update_users()
        return new_record

    def write(self, vals):
        res = super(ResUsersRole, self).write(vals)
        self.update_users()
        return res

    def unlink(self):
        users = self.mapped("user_ids")
        for record in self:
            if self.env.ref('member_minor_configuration.member_group_city_admin').id in record.implied_ids._origin.ids:
                raise UserError(_("Member City Administrator has a Role Can't Be Deleted"))
            if self.env.ref('member_minor_configuration.member_group_admin').id in record.implied_ids._origin.ids:
                raise UserError(_("Member Sub City Administrator has a Role Can't Be Deleted"))
            if self.env.ref('member_minor_configuration.member_group_manager').id in record.implied_ids._origin.ids:
                raise UserError(_("Member Woreda Administrator has a Role Can't Be Deleted"))

            if self.env.ref('member_minor_configuration.member_group_main_manager').id in record.implied_ids._origin.ids:
                raise UserError(_("Member Basic Organization Administrator has a Role Can't Be Deleted"))
            if self.env.ref('member_minor_configuration.member_group_main_assembler').id in record.implied_ids._origin.ids:
                raise UserError(_("Member Basic Organization Assembler has a Role Can't Be Deleted"))
            if self.env.ref('member_minor_configuration.member_group_main_finance').id in record.implied_ids._origin.ids:
                raise UserError(_("Member Basic Organization Finance has a Role Can't Be Deleted"))

            if self.env.ref('member_minor_configuration.member_group_cell_manager').id in record.implied_ids._origin.ids:
                raise UserError(_("Member Cell Administrator has a Role Can't Be Deleted"))
            if self.env.ref('member_minor_configuration.member_group_assembler').id in record.implied_ids._origin.ids:
                raise UserError(_("Member Cell Assembler has a Role Can't Be Deleted"))
            if self.env.ref('member_minor_configuration.member_group_finance').id in record.implied_ids._origin.ids:
                raise UserError(_("Member Cell Finance has a Role Can't Be Deleted"))

            if self.env.ref('base.group_portal').id in record.implied_ids._origin.ids:
                raise UserError(_("Portal User has a Role Can't Be Deleted"))
            if self.env.ref('base.group_user').id in record.implied_ids._origin.ids:
                raise UserError(_("Internal User has a Role Can't Be Deleted"))
        res = super(ResUsersRole, self).unlink()
        users.set_groups_from_roles(force=True)
        return res

    def update_users(self):
        """Update all the users concerned by the roles identified by `ids`."""
        users = self.mapped("user_ids")
        users.set_groups_from_roles()
        return True

    @api.model
    def cron_update_users(self):
        logging.info("Update user roles")
        self.search([]).update_users()


class ResUsersRoleLine(models.Model):
    _name = "res.users.role.line"
    _description = "Users associated to a role"

    active = fields.Boolean(related="user_id.active")
    role_id = fields.Many2one(
        comodel_name="res.users.role", required=True, string="Role", ondelete="cascade"
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        required=True,
        string="User",
        domain=[("id", "!=", SUPERUSER_ID)],
        ondelete="cascade",
    )
    date_from = fields.Date("From")
    date_to = fields.Date("To")
    is_enabled = fields.Boolean(default=True, store=True)
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.user.company_id
    )

    @api.constrains("user_id", "company_id")
    def _check_company(self):
        for record in self:
            if (
                record.company_id
                and record.company_id != record.user_id.company_id
                and record.company_id not in record.user_id.company_ids
            ):
                raise ValidationError(
                    _('User "{}" does not have access to the company "{}"').format(
                        record.user_id.name, record.company_id.name
                    )
                )

    @api.depends("date_from", "date_to")
    def _compute_is_enabled(self):
        today = datetime.date.today()
        for role_line in self:
            role_line.is_enabled = True
            if role_line.date_from:
                date_from = role_line.date_from
                if date_from > today:
                    role_line.is_enabled = False
            if role_line.date_to:
                date_to = role_line.date_to
                if today > date_to:
                    role_line.is_enabled = False

    def unlink(self):
        users = self.mapped("user_id")
        res = super(ResUsersRoleLine, self).unlink()
        users.set_groups_from_roles(force=True)
        return res
