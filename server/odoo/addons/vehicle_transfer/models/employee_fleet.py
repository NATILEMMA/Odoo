from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime


class FleetChecklistEvaluateInitial(models.Model):
    _inherit = 'fleet.checklistevaluate.initial'
    _description = 'checklist category'

    employee = fields.Many2one('employee.fleet', string='reverse')

class FleetChecklistEvaluateFinal(models.Model):
    _inherit = 'fleet.checklistevaluate.final'
    _description = 'checklist category'

    employee = fields.Many2one('employee.fleet', string='reverse')


class FleetReservedTime(models.Model):
    _name = "fleet.reserved"
    _description = "Reserved Time"

    employee = fields.Many2one('res.partner', string='Employee')
    date_from = fields.Date(string='Reserved Date From')
    date_to = fields.Date(string='Reserved Date To')
    reserved_obj = fields.Many2one('fleet.vehicle')


class FleetVehicleInherit(models.Model):
    _inherit = 'fleet.vehicle'

    check_availability = fields.Boolean(default=True, copy=False)
    reserved_time = fields.One2many('fleet.reserved', 'reserved_obj', String='Reserved Time', readonly=1,
                                    ondelete='cascade')


class EmployeeFleet(models.Model):
    _name = 'employee.fleet'
    _description = 'Employee Vehicle Request'
    _inherit = 'mail.thread'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.fleet')
        
        return super(EmployeeFleet, self).create(vals)


    def send(self):
        if self.date_from:
            # fleet_obj = self.env['fleet.vehicle'].search([])
            check_availability = 0
#             for i in fleet_obj:
#                 for each in i.reserved_time:
#                     if each.date_from and each.date_to:
#                         if each.date_from <= self.date_from <= each.date_to:
#                             check_availability = 1
#                         elif self.date_from < each.date_from:
#                             if each.date_from <= self.date_to <= each.date_to:
#                                 check_availability = 1
#                             elif self.date_to > each.date_to:
#                                 check_availability = 1
#                             else:            self.checklist = checklist

#                                 check_availability = 0
#                         else:
#                             check_availability = 0
            if self.fleet:
               if self.fleet.driver_id:
                   raise Warning('The vehicle has Diver. please return from to submit request')
            if self.date_to:
                date = self.date_to
            else:
                date = datetime.now().date()
            if check_availability == 0:
                reserved_id = self.fleet.reserved_time.create({'employee': self.employee.id,
                                                               'date_from': self.date_from,
                                                               'date_to': self.date_to,
                                                               'reserved_obj': self.fleet.id,
                                                               })
                self.write({'reserved_fleet_id': reserved_id.id})
                self.state = 'waiting'
            else:
                raise Warning('Sorry This vehicle is already requested by another employee')

    @api.onchange('checklist_template')
    def get_checklist_line(self):
        print("onchange")
        self.checklist = [(5, 0, 0)]
        checklist = []
        if self.checklist_template:
            for checklist_type in self.checklist_template.checklist:
                checklist.append((0, 0, {'checklist_id': checklist_type.id}))
            print("checklist", checklist_type)
            self.checklist = checklist
            self.checklist_2 = checklist

    def approve(self):
        self.fleet.fleet_status = True
        self.state = 'confirm'
        self.fleet.driver_id = self.employee.id
        self.fleet.driver_status = 'occupied'
        mail_content = _('Hi %s,<br>Your vehicle request for the reference %s is approved.') % \
                        (self.employee.name, self.name)
        main_content = {
            'subject': _('%s: Approved') % self.name,
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': self.employee.email,
        }
        mail_id = self.env['mail.mail'].create(main_content)
        mail_id.mail_message_id.body = mail_content
        mail_id.send()
        if self.employee.user_id:
            # mail_id.mail_message_id.write({'needaction_partner_ids': [(4, self.employee.user_id.partner_id.id)]})
            mail_id.mail_message_id.write({'partner_ids': [(4, self.employee.user_id.partner_id.id)]})

    # @api.multi
    def reject(self):
        self.reserved_fleet_id.unlink()
        self.state = 'reject'
        mail_content = _('Hi %s,<br>Sorry, Your vehicle request for the reference %s is Rejected.') % \
                        (self.employee.name, self.name)

        main_content = {
            'subject': _('%s: Approved') % self.name,
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': self.employee.work_email,
        }
        mail_id = self.env['mail.mail'].create(main_content)
        mail_id.mail_message_id.body = mail_content
        mail_id.send()
        if self.employee.user_id:
            # mail_id.mail_message_id.write({'needaction_partner_ids': [(4, self.employee.user_id.partner_id.id)]})
            mail_id.mail_message_id.write({'partner_ids': [(4, self.employee.user_id.partner_id.id)]})

    # @api.multi
    def cancel(self):
        if self.reserved_fleet_id:
            self.reserved_fleet_id.unlink()
        self.state = 'cancel'

    # @api.multi
    def returned(self):
        self.reserved_fleet_id.unlink()
        self.returned_date = fields.datetime.now().date()
        self.state = 'return'
        print("self.employee.driver_id", self.fleet.driver_id)
        self.fleet.driver_id = False
        self.fleet.driver_status = 'free'
        print("self.employee.driver_id after false", self.fleet.driver_id)

    @api.constrains('date_from', 'date_to')
    def onchange_date_to(self):
        for each in self:
          if each.date_from and each.date_to:
            if each.date_from > each.date_to:
                raise Warning('Date To must be greater than Date From')

    @api.onchange('date_from', 'date_to')
    def check_availability(self):
        if self.date_from and self.date_to:
            self.fleet = ''
            fleet_obj = self.env['fleet.vehicle'].search([])
            for i in fleet_obj:
                for each in i.reserved_time:
                    if each.date_from and each.date_to:
                        if each.date_from <= self.date_from <= each.date_to:
                            i.write({'check_availability': False})
                        elif self.date_from < each.date_from:
                            if each.date_from <= self.date_to <= each.date_to:
                                i.write({'check_availability': False})
                            elif self.date_to > each.date_to:
                                i.write({'check_availability': False})
                            else:
                                i.write({'check_availability': True})
                        else:
                            i.write({'check_availability': True})

    reserved_fleet_id = fields.Many2one('fleet.reserved', invisible=1, copy=False)
    checklist_template = fields.Many2one('fleet.checklist.template', string='Checklist Template')
    name = fields.Char(string='Request Number', copy=False,translate=True)
    employee = fields.Many2one('res.partner', string='Driver', required=1, readonly=True,
                               states={'draft': [('readonly', False)]})
    req_date = fields.Date(string='Requested Date', default=fields.Date.context_today, required=1,
                           states={'draft': [('readonly', False)]}, help="Requested Date")
    fleet = fields.Many2one('fleet.vehicle', string='Vehicle', required=1, readonly=True,
                            states={'draft': [('readonly', False)]})
    date_from = fields.Date(string='From',  readonly=True,
                                states={'draft': [('readonly', False)]}, default =  fields.Date.today())
    date_to = fields.Date(string='To',  readonly=True,
                              states={'draft': [('readonly', False)]})
    returned_date = fields.Date(string='Returned Date', readonly=1)
    purpose = fields.Text(string='Additional Note', required=1, readonly=True,
                          states={'draft': [('readonly', False)]}, help="Purpose",translate=True)
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting for Approval'), ('cancel', 'Cancel'),
                              ('confirm', 'Approved'), ('reject', 'Rejected'), ('return', 'Returned')],
                             string="State", default="draft")

    checklist = fields.One2many('fleet.checklistevaluate.initial', 'employee',
                                string='Checklist Lines')
    checklist_2 = fields.One2many('fleet.checklistevaluate.final', 'employee',
                                string='Checklist Lines')

    engine_oil = fields.Selection([('pass', 'Pass'), ('fail', 'Failed')],
                             string="Engine Oil")
    brake_fluid = fields.Selection([('pass', 'Pass'), ('fail', 'Failed')],
                             string="Brake Fluid")
    radiator_fluid = fields.Selection([('pass', 'Pass'), ('fail', 'Failed')],
                             string="Radiator Fluid")
    battery_water = fields.Selection([('pass', 'Pass'), ('fail', 'Failed')],
                             string="Battrey Water")
    window = fields.Selection([('pass', 'Pass'), ('fail', 'Failed')],
                             string="Windows")
    fuel_level = fields.Selection([('pass', 'Pass'), ('fail', 'Failed')],
                             string="Fuel Level")

    @api.model
    def default_get(self, fields):
        res = super(EmployeeFleet, self).default_get(fields)
        vehical_obj = self.env['fleet.vehicle']
        if self._context.get('active_id', False):
            vehicle = vehical_obj.browse(self._context['active_id'])
            res.update({
                        'fleet': self._context['active_id'] or False})


        return res


