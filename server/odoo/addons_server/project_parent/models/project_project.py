
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)
class Project(models.Model):
    _inherit = "project.project"
    _parent_store = True
    _parent_name = "parent_id"

    parent_id = fields.Many2one(
        comodel_name="project.project", string="Parent Planning", index=True
    )
    child_ids = fields.One2many(
        comodel_name="project.project", inverse_name="parent_id", string="Sub-projects"
    )

    parent_path = fields.Char(index=True)
    parent_path2 = fields.Char(compute="_compute_path",store=True)
    is_parent = fields.Boolean(compute="_compute_child", store=True)

    child_ids_count = fields.Integer(compute="_compute_child_ids_count", store=True)
    
    @api.onchange('department_id')
    def _onchange_department(self):
        _logger.info("###########_onchange_department#############")
        members = self.env['hr.employee'].search([('department_id','=',self.department_id.id)])
        _logger.info("###########members############# %s",members)
        members_list = []
        if  members:
            for line in members:
                members_list.append(line.id)
            self.user_ids = [(6,0,members_list)]

        
    def set_parent_path(self,parent_project):
        path=""
        new_path=""
        _logger.info("======@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@get_name======%s",parent_project)
        parent=parent_project
        while True:
            _logger.info("=====*********************=$$$$$$$parent======%s",parent)
            if parent:
                path=path+"/"+parent.name
                parent=parent.parent_id
                _logger.info("======$$$$$$$path======%s",path)
            else:
                perv_path=path.split('/')
                _logger.info("======START REVERSE=====%s",perv_path)
                for i in reversed(perv_path):
                    _logger.info("====== i=====%s",i)
                    new_path=new_path+"/"+i 
                _logger.info("======$$$$$$$new_path======%s",new_path)
                return new_path
    
    def check_child(self):
        _logger.info("======START CHILD")
        projects = self.env['project.project'].search([]).ids
        for project in self.env['project.project'].browse(projects):
            set_parent_path=self.set_parent_path(project.parent_id)
            project.parent_path=set_parent_path
        _logger.info("======END CHILD")

    def get_name(self):
        
        # self.check_child()
        for project in self:
            
            _logger.info("======$$$$$$$project======%s",project)
            # _logger.info("======$$$$$$$get_name======%s",project.parent_id)
            parent=project.parent_id
            return self.set_parent_path(parent)
    # @api.onchange('parent_id',"child_ids")
    # def _change_path(self):
    #     # for project in self:
    #     path=""
        
    #     projects = self.env['project.project'].search([('id', '=', self.parent_id.id)]).ids
    #     for project in self.env['project.project'].browse(projects):
    #         if project.parent_id:
    #             _logger.info("=====***************======%s",project.parent_id)
                
    #             name=self.get_name(project.parent_id)
    #             path=path + name
            
    #             _logger.info("======$$$$$$$path======%s",path)
    #     _logger.info("======$$$$$$$$$$####path%s",path)
    #     self.parent_path2=path
    @api.depends("child_ids","parent_id")
    def _compute_path(self):
        for project in self:
            path=""
            path=project.get_name()
            _logger.info("======$$$$$$$$$$####path%s",path)
            _logger.info("======$$$$$$$$$$####project.parent_path2 %s",project.parent_path2 )
            project.parent_path2 =path
        # for project in self:
        # #     path=""
        # #     parent_path=project.parent_path
        # #     if parent_path:
        # #         perv_path=parent_path.split('/')
        # #         _logger.info("===========project.parent_path%s",project.parent_path)
        # #         _logger.info("===========perv_path%s",perv_path)
        # #         _logger.info("======######path%s",path)

        # #         for path_val in perv_path:
        # #             if path_val:
        # #                 perv_path
        # #                 name = self.env['project.project'].search([('id', '=', int(path_val))]).name
        # #                 _logger.info("===========name%s",name)
        # #                 _logger.info("===========path%s",path)
        # #                 path=path+"/"+name
        # #     _logger.info("======$$$$$$$$$$####path%s",path)
        # #     project.parent_path2=path
            
        #     _logger.info("=====project***************======%s",project.id)
        #     _logger.info("=====project--***************======%s",project)
        #     projects = self.env['project.project'].search([('id', '=', self.id)]).ids
        #     for project in self.env['project.project'].browse(projects):
        #         if project.parent_id:
        #             _logger.info("=====Depend***************======%s",project.parent_id)
                    
        #             name=project.parent_id.name
        #             path=path +"/"+ name
        #             name=self.get_name(project.parent_id)
        #             if name:
        #                 name=self.get_name(project.parent_id)
        #             _logger.info("======$$$$$$$path======%s",path)
        #     _logger.info("======$$$$$$$$$$####path%s",path)
        #     self.parent_path2=path

    
    @api.depends("child_ids")
    def _compute_child(self):
        for project in self:
            if len(project.child_ids) >0:
                project.is_parent = True
            else:
                project.is_parent = False

    @api.depends("child_ids")
    def _compute_child_ids_count(self):
        for project in self:
            project.child_ids_count = len(project.child_ids)

    def action_open_child_project(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx.update(default_parent_id=self.id)
        domain = [("parent_id", "=", self.id)]
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "name": "Children of %s" % self.name,
            "view_mode": "tree,form,graph",
            "res_model": "project.project",
            "target": "current",
            "context": ctx,
            "domain": domain,
        }
