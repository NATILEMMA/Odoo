
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class FleetVehicleModel(models.Model):
    
    _inherit = 'fleet.vehicle.model'
    income_acc_id = fields.Many2one("account.account",
                                    string="Income Account")
    expence_acc_id = fields.Many2one("account.account",
                                     string="Expense Account")

class ChecklistCategory(models.Model):
    
    _name = 'checklist.category'
    _description = 'checklist category'
    

    name = fields.Char('Name')
    parent_category = fields.Many2one('checklist.category','Parent Category')
    code = fields.Char(string='Code')

class FleetChecklist(models.Model):
    
    _name = 'fleet.checklist'
    _description = 'checklist category'
    

    name = fields.Char('Name')
    category_id = fields.Many2one('checklist.category','Category')
    template_id = fields.Many2one('fleet.checklist.template',invisible=1)

class FleetChecklistEvaluate(models.Model):
    
    _name = 'fleet.checklistevaluate'
    _description = 'checklist category'
    
    service_id = fields.Many2one('fleet.vehicle.log.services')
    checklist_id = fields.Many2one('fleet.checklist','Checklist')
    ok = fields.Boolean('OK')
    defect = fields.Boolean('Defect')
    fixed = fields.Boolean('fixed')
    remark = fields.Char('Remark')


    # passed = fields.Boolean('Passed')
    # repaired = fields.Boolean('Repaired')
    # replaced = fields.Boolean('Replaced')
    # n_a = fields.Boolean('N/A')


class FleetChecklistTemplate(models.Model):
    
    _name = 'fleet.checklist.template'

    name = fields.Char('Name')
    # checklist = fields.One2many('fleet.checklist', 'template_id',
    #                                   string='Checklist Lines')
    checklist = fields.Many2many('fleet.checklist',
                                       'fleet_checklist_rel',
                                       'tempate_id', 'checklist_id',
                                       string='Checklist Lines')


                                    #   fleet.checklist.template