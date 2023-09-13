
import random
import string
import werkzeug.urls
from odoo import tools
from collections import defaultdict
from datetime import datetime, date 
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
from odoo.exceptions import UserError, Warning, ValidationError

import logging
_logger = logging.getLogger(__name__)
pick1 = []
pick2 = []
pick3 = []
pick4 = []

class UsersRole(models.Model):
    _inherit = "res.users.role"
    
    
    def write(self,vals):
    
        search_val = self.env['res.users.role'].sudo().search([('id','=',self.id)],limit=1)
        get_gergory_role = self.env['res.users.role'].sudo().search([('name','=','Gregorian datepicker role')], limit=1)
        get_ethiopian_role = self.env['res.users.role'].sudo().search([('name','=','Ethiopian datepicker role')], limit=1)
        if get_gergory_role.id == search_val.id:
            raise ValidationError(_("You cannot edit/update this role because it is built into the system"))
        if get_ethiopian_role.id == search_val.id:
            raise ValidationError(_("You cannot edit/update this role because it is built into the system"))
        res = super(UsersRole,self).write(vals)
        return res
    
    
    def unlink(self):
       
        search_val = self.env['res.users.role'].search([('id','=',self.id)],limit=1)
        get_gergory_role = self.env['res.users.role'].sudo().search([('name','=','Gregorian datepicker role')], limit=1)
        get_ethiopian_role = self.env['res.users.role'].sudo().search([('name','=','Ethiopian datepicker role')], limit=1)
        if get_gergory_role.name == search_val.name:
            raise ValidationError(_("You cannot delete/remove this role because it is built into the system."))
        if get_ethiopian_role.name == search_val.name:
            raise ValidationError(_("You cannot delete/remove this role because it is built into the system."))
        res = super().unlink()
        return res
    

class ResUsersRole(models.Model):
    _inherit = "res.users.role.line"

    is_active = fields.Boolean(default=False)




class ResUsers(models.Model):
    _inherit = 'res.users'


    is_ethiopian_datepicker = fields.Boolean(string="Ethiopian Datepicker")

    # def write(self,vals):
    #     res = super(ResUsers, self).write(vals)
    #     try:
    #         search = self.env['res.users'].sudo().search([('id','in',self.ids)])
    #         for line in search.role_line_ids:
    #             if line.role_id.name == 'Ethiopian datepicker role':
    #                 line.sudo().write({'is_enabled': False})
    #     except:
    #         pass
        # return res


    def transfer_node_to_modifiers(node, modifiers, context=None, in_tree_view=False):
        if node.get('attrs'):
            #If you want, add more conditions here
            if ', uid' in  node.get('attrs'):
                user_id = str(context.get('uid', 1))
                user_id = ', ' + user_id
                attrs = node.get('attrs')
                attrs = attrs.replace(', uid', user_id)
                node.set('attrs', attrs)
            modifiers.update(eval(node.get('attrs')))

        if node.get('states'):
            if 'invisible' in modifiers and isinstance(modifiers['invisible'], list):
                # TODO combine with AND or OR, use implicit AND for now.
                modifiers['invisible'].append(('state', 'not in', node.get('states').split(',')))
            else:
                modifiers['invisible'] = [('state', 'not in', node.get('states').split(','))]

        for a in ('invisible', 'readonly', 'required'):
            if node.get(a):
                v = bool(eval(node.get(a), {'context': context or {}}))
                if in_tree_view and a == 'invisible':
                    # Invisible in a tree view has a specific meaning, make it a
                    # new key in the modifiers attribute.
                    modifiers['tree_invisible'] = v
                elif v or (a not in modifiers or not isinstance(modifiers[a], list)):
                    # Don't set the attribute to False if a dynamic value was
                    # provided (i.e. a domain from attrs or states).
                    modifiers[a] = v

    @api.model
    def initial_date(self, data):
            return False
           
    

    # @api.onchange('is_ethiopian_datepicker')
    # def onchange_ethiopiandatepicker(self):
    #     """ 
    #                 Duplicate Only The SQL Query and replace your model name

    #     """
    #     if self.is_ethiopian_datepicker == True:
    #         query = """
    #             update  reconciliation_time_fream  set  is_ethiopian_datepicker=%s where id=id
    #         """ %(True)
            

    #         cr = self._cr
    #         # cr.execute(query)
    #         ethio_groups = self.env['res.groups'].search([('name','=','Ethiopian Datepicker')], limit=1)
    #         gro_groups = self.env['res.groups'].search([('name','=','Gregory Datepicker')], limit=1)
    #         ethio_user_list = []
    #         gro_user_list = []

    #         _logger.info(" ###### ethio_groups %s",ethio_groups.users)
    #         _logger.info(" ###### gro_groups %s",gro_groups.users)

    #         if ethio_groups.users is not None:
    #             if self.env.user in ethio_groups.users: 
    #                 for user in gro_groups.users:
    #                     if self.env.user.id == user.id:
    #                         pass
    #                     else:
    #                         gro_user_list.append(user.id)
    #                 for users in ethio_groups.users:
    #                     ethio_user_list.append(users.id)
    #             else:
    #                 for users in ethio_groups.users:
    #                     ethio_user_list.append(users.id)
    #                 for user in gro_groups.users:
    #                     _logger.info(" ###### gro_groups %s",user.name)

    #                     if self.env.user.id == user.id:
    #                         _logger.info(" ###### TTT %s",user.name)

    #                         pass
    #                     else:
    #                         _logger.info(" ###### FF %s",user.name)

    #                         gro_user_list.append(user.id)
    #                 ethio_user_list.append(self.env.user.id)

    #             _logger.info(" ###### ethio_user_list %s",ethio_user_list)
    #             _logger.info(" ###### gro_user_list %s",gro_user_list)
                
    #             ethio_groups['users'] = [(6,0,ethio_user_list)]
    #             gro_groups['users'] = [(6,0,gro_user_list)]
            
    #         else:
    #             pass


    #         self.is_ethiopian_datepicker = True

     
    #     if self.is_ethiopian_datepicker == False:
    #         query = """
    #             update  reconciliation_time_fream  set is_ethiopian_datepicker = %s where id=id
    #         """ %(False)

    #         cr = self._cr
    #         # cr.execute(query)
    #         ethio_groups = self.env['res.groups'].search([('name','=','Ethiopian Datepicker')], limit=1)
    #         gro_groups = self.env['res.groups'].search([('name','=','Gregory Datepicker')], limit=1)
    #         ethio_user_list = []
    #         gro_user_list = []
    #         if gro_groups.users is not None:
           

                
    #             if self.env.user in gro_groups.users: 
    #                 for user in ethio_groups.users:
    #                     if self.env.user.id == user.id:
    #                         pass
    #                     else:
    #                         ethio_user_list.append(user.id)
    #                 for users in gro_groups.users:
    #                     gro_user_list.append(users.id)
    #             else:
    #                 for users in gro_groups.users:
    #                     gro_user_list.append(users.id)
    #                 for user in ethio_groups.users:
    #                     _logger.info(" ###### gro_groups %s",user.name)

    #                     if self.env.user.id == user.id:
    #                         _logger.info(" ###### TTT %s",user.name)

    #                         pass
    #                     else:
    #                         _logger.info(" ###### FF %s",user.name)

    #                         ethio_user_list.append(user.id)
    #                 gro_user_list.append(self.env.user.id)

    #             _logger.info(" ###### ethio_user_list %s",ethio_user_list)
    #             _logger.info(" ###### gro_user_list %s",gro_user_list)
                
    #             ethio_groups['users'] = [(6,0,ethio_user_list)]
    #             gro_groups['users'] = [(6,0,gro_user_list)]
            

                # if self.env.user in gro_groups.users: 
                #     for user in ethio_groups.users:
                #         if self.env.user.id == user.id:
                #             pass
                #         else:
                #             ethio_user_list.append(user.id)
                #     for users in gro_groups.users:
                #         gro_user_list.append(users.id)
                # else:
                #     _logger.info("Nnnnnnnnnnnnn in gre")
                #     for user_e in ethio_groups.users:
                #         _logger.info("^^^^^^^^^^^^ %s",user_e.name)
                #         if self.env.user.id == user_e.id:
                #             pass
                #         else:
                #             ethio_user_list.append(user_e.id)
                #     for users in gro_groups.users:
                #         gro_user_list.append(users.id)
                    
                #     gro_user_list.append(self.env.user.id)
                # _logger.info("gro_user_list in gre %s",gro_user_list)
                # _logger.info("ethio_user_list in gre %s",ethio_user_list)

              

                # ethio_groups['users'] = [(6,0,ethio_user_list)]
                # gro_groups['users'] = [(6,0,gro_user_list)]
            # else:
            #     pass

            # self.is_ethiopian_datepicker = False
    # @api.model
    # def initial_datepicker_value(self, data):
    #     User = self.env['res.users']
    #     current_user = User.browse(self.env.uid)
    #     data = current_user.is_ethiopian_datepicker
    #     _logger.info("################# Initial Datepicker Value %s", data)
    #     return data


    @api.model
    def onchange_ethiopiandatepicker_from_checkbox(self,checkedvalue):
        _logger.info("******* checkedvalue ******,%s",checkedvalue)

        get_user = self.env.user
        for role in get_user.role_line_ids:
            if checkedvalue['value'] == 'True' and role.role_id.name == 'Ethiopian datepicker role':
                _logger.info("Etho--------------")
                
                val = {}
                val['id'] = get_user.id
                val['role_id'] = role.role_id.id
                val['value']= checkedvalue['value']
                # get_user.role_line_ids.sudo().write(val)
                # role._compute_is_enabled(val)
                role.is_active = True
                gregorian_role = self.env['res.users.role'].sudo().search([('name','=','Gregorian datepicker role')], limit=1)
                get_ethiopia_role = self.env['res.users.role.line'].sudo().search([('user_id','=',get_user.id),('role_id','=',role.role_id.id)], limit=1)
                get_gregory_role = self.env['res.users.role.line'].sudo().search([('user_id','=',get_user.id),('role_id','=',gregorian_role.id)], limit=1)
                _logger.info("get_role gregorian_role#### %s",gregorian_role)

                if val.get('value') == 'True': 
                    _logger.info("*******TTTTT********")
                    get_gregory_role.is_enabled = False
                    get_ethiopia_role.is_enabled = True
                    get_ethiopia_role.sudo().write({'is_enabled': True})
                    get_gregory_role.sudo().write({'is_enabled': False})
                    get_user.is_ethiopian_datepicker = True
                    self.env.cr.commit()
           

            if checkedvalue['value'] == 'False' and role.role_id.name == 'Gregorian datepicker role':
                _logger.info("Gregorrrrr--------------")
                val = {}
                val['id'] = get_user.id
                val['role_id'] = role.role_id.id
                val['value']= checkedvalue['value']
                role.is_active = False
                ethiopian_role = self.env['res.users.role'].sudo().search([('name','=','Ethiopian datepicker role')], limit=1)
                get_gregory_role = self.env['res.users.role.line'].sudo().search([('user_id','=',get_user.id),('role_id','=',role.role_id.id)], limit=1)
                get_ethiopia_role = self.env['res.users.role.line'].sudo().search([('user_id','=',get_user.id),('role_id','=',ethiopian_role.id)], limit=1)

                _logger.info("get_role ethiopian_role#### %s",ethiopian_role)
                if val.get('value') == 'False': 
                    _logger.info("******TTTTTT****")
                    get_gregory_role.is_enabled = True
                    get_ethiopia_role.is_enabled = False
                    get_gregory_role.sudo().write({'is_enabled': True})
                    get_user.is_ethiopian_datepicker = False
                    self.env.cr.commit()

                    






        
        # if checkedvalue['value'] == 'True':

        #     query = """
        #         update  reconciliation_time_fream  set  is_ethiopian_datepicker=%s where id=id
        #     """ %(True)
            

        #     cr = self._cr
        #     # cr.execute(query)
        #     ethio_groups = self.env['res.groups'].search([('name','=','Ethiopian Datepicker')], limit=1)
        #     gro_groups = self.env['res.groups'].search([('name','=','Gregory Datepicker')], limit=1)
        #     ethio_user_list = []
        #     gro_user_list = []

        #     _logger.info(" ###### ethio_groups %s",ethio_groups.users)
        #     _logger.info(" ###### gro_groups %s",gro_groups.users)

        #     if ethio_groups.users is not None:
        #         if self.env.user in ethio_groups.users: 
        #             for user in gro_groups.users:
        #                 if self.env.user.id == user.id:
        #                     pass
        #                 else:
        #                     gro_user_list.append(user.id)
        #             for users in ethio_groups.users:
        #                 ethio_user_list.append(users.id)
        #         else:
        #             for users in ethio_groups.users:
        #                 ethio_user_list.append(users.id)
        #             for user in gro_groups.users:
        #                 _logger.info(" ###### gro_groups %s",user.name)

        #                 if self.env.user.id == user.id:
        #                     _logger.info(" ###### TTT %s",user.name)

        #                     pass
        #                 else:
        #                     _logger.info(" ###### FF %s",user.name)

        #                     gro_user_list.append(user.id)
        #             ethio_user_list.append(self.env.user.id)

        #         _logger.info(" ###### ethio_user_list %s",ethio_user_list)
        #         _logger.info(" ###### gro_user_list %s",gro_user_list)
                
        #         ethio_groups['users'] = [(6,0,ethio_user_list)]
        #         gro_groups['users'] = [(6,0,gro_user_list)]
            
        #     else:
        #         pass


        #     self.is_ethiopian_datepicker = True

     
        # if checkedvalue['value'] == 'False':
        #     query = """
        #         update  reconciliation_time_fream  set is_ethiopian_datepicker = %s where id=id
        #     """ %(False)

        #     cr = self._cr
        #     # cr.execute(query)
        #     ethio_groups = self.env['res.groups'].search([('name','=','Ethiopian Datepicker')], limit=1)
        #     gro_groups = self.env['res.groups'].search([('name','=','Gregory Datepicker')], limit=1)
        #     ethio_user_list = []
        #     gro_user_list = []
        #     if gro_groups.users is not None:
           

                
        #         if self.env.user in gro_groups.users: 
        #             for user in ethio_groups.users:
        #                 if self.env.user.id == user.id:
        #                     pass
        #                 else:
        #                     ethio_user_list.append(user.id)
        #             for users in gro_groups.users:
        #                 gro_user_list.append(users.id)
        #         else:
        #             for users in gro_groups.users:
        #                 gro_user_list.append(users.id)
        #             for user in ethio_groups.users:
        #                 _logger.info(" ###### gro_groups %s",user.name)

        #                 if self.env.user.id == user.id:
        #                     _logger.info(" ###### TTT %s",user.name)

        #                     pass
        #                 else:
        #                     _logger.info(" ###### FF %s",user.name)

        #                     ethio_user_list.append(user.id)
        #             gro_user_list.append(self.env.user.id)

        #         _logger.info(" ###### ethio_user_list %s",ethio_user_list)
        #         _logger.info(" ###### gro_user_list %s",gro_user_list)
                
        #         ethio_groups['users'] = [(6,0,ethio_user_list)]
        #         gro_groups['users'] = [(6,0,gro_user_list)]
        
        #     else:
        #         pass

        #     self.is_ethiopian_datepicker = False



class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    is_ethiopian_datepicker = fields.Boolean()
   


   
    # def set_values(self):
    #     _logger.info("############################## %s",self.is_ethiopian_datepicker)
    #     res = super(ResConfigSettings, self).set_values()
    #     self.env['ir.config_parameter'].set_param('EthiopianCalendar.is_ethiopian_datepicker', self.is_ethiopian_datepicker)
    #     return res

    # @api.onchange('is_ethiopian_datepicker')
    # def onchange_ethiopiandatepicker(self):
    #     """ 
    #                 Duplicate Only The SQL Query and replace your model name

    #     """

    #     # tools.drop_view_if_exists(self._cr, 'reconciliation_time_fream')
    #     if self.is_ethiopian_datepicker == True:
    #         query = """
    #             update  reconciliation_time_fream  set ticked_user	= %s  where id=id
    #         """ %(self.env.user.id)

    #         cr = self._cr
    #         cr.execute(query)

    #         users = self.env['res.partner'].search([('user_id','=',self.env.user.id)], limit=1)
    #         _logger.info("############## %s",users)
    #         _logger.info("############## %s", users.ticked_user)

    #         # users = users.ticked_user
    #         # line_value_2.account_ids = [(6,0,values)]
    #         # self.env.cr.commit()
    #     if self.is_ethiopian_datepicker == False:
    #         query = """
    #             update  reconciliation_time_fream  set is_ethiopian_datepicker	= %s  where id=id
    #         """ %(False)

    #         cr = self._cr
    #         cr.execute(query)
    #         self.is_ethiopian_datepicker = False
    #         # self.env.cr.commit()


        

    
class FiscalYear(models.Model):
    _inherit = 'fiscal.year'

    """ 
    """

    ethiopian_to = fields.Date(string="in ethiopian date")
    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    pagum_to = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')
    is_pagum_to = fields.Boolean(default='True',string="in ethiopian date")
 
    
    @api.model
    def create(self, vals):

        """
            Use this for loop to get your most recently selected date from the global append Ethiopian date.

            if your widget type are

            - ethiopian_calander_widget user pick1
            - ethiopian_calander_widget_two user pick2
            - ethiopian_calander_widget_three user pick3
            - ethiopian_calander_widget_four user pick4
           
       Pick1 is used in the for loop below because my view displays an Ethiopian date picker using the *ethiopian_calander_widget* widget type.

        """
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                _logger.info("^^^^^^^^^^^ %s",type(Edate1))
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['date_from'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False

                        pick1.clear()
                    if type(Edate1) ==   date:
                        vals['date_from'] = date1
                        vals['ethiopian_from'] = Edate1
                        pick1.clear()
                
        for i in range(0, len(pick2)):
        
            if i == (len(pick2)-1):
                date2 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
                Edate2 = EthiopianDateConverter.to_ethiopian(date2.year,date2.month,date2.day)
                _logger.info("^^^^^^^^^^^ %s",type(Edate2))

                if pick2[i]['pick'] == 2:
                    if type(Edate2) ==   str:
                        vals['ethiopian_to'] = None
                        vals['date_to'] = date2
                        vals['pagum_to'] = Edate2
                        vals['is_pagum_to'] = False

                        pick2.clear()
                    if type(Edate2) ==   date:
                        vals['date_to'] = date2
                        vals['ethiopian_to'] = Edate2
                        pick2.clear()
        try:
            if vals['date_from'] is not None and vals['date_to'] is not None:
                date1 = vals['date_from']
                date2 = vals['date_to']
                date_time_obj = date1.split('-')
                date_time_obj2 = date2.split('-')

                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate2 = EthiopianDateConverter.to_ethiopian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
                _logger.info("^^^^^^^^^^^ %s",type(Edate1))
                _logger.info("^^^^^^^^^^^ %s",type(Edate2))
                if type(Edate1) ==   date and type(Edate2) ==   date:
                    vals['ethiopian_from'] = Edate1
                    vals['ethiopian_to'] = Edate2
                elif type(Edate1) == date and type(Edate2) == str:
                    vals['ethiopian_from'] = Edate1
                    vals['pagum_to'] = Edate2
                    vals['is_pagum_to'] = False

                elif type(Edate1) ==   str and type(Edate2) ==   date:
                    vals['pagum_from'] = Edate1
                    vals['ethiopian_to'] = Edate2
                    vals['is_pagum_from'] = False

                elif type(Edate1) ==   str and type(Edate2) ==   str:
                    vals['pagum_from'] = Edate1
                    vals['pagum_to'] = Edate2
                    vals['is_pagum_from'] = False
                    vals['is_pagum_to'] = False

                else:
                    pass
        except:
            pass
       
        return super(FiscalYear, self).create(vals)


    
    def write(self, vals):
        _logger.info("########dd##### Write:%s",vals)
        
        """
            This try-catch method is used to convert the Gregorian calendar to the Ethiopian calendar.
        
        """
        try:
            if vals['ethiopian_from'] is not None:
                date_str = vals['ethiopian_from']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date_from'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_from'] = Edate1
                        vals['pagum_from'] = None
                        vals['is_pagum_from'] = True
        except:
            pass
        try:
            if vals['ethiopian_to'] is not None:
                date_str = vals['ethiopian_to']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date_to'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_to'] = None
                        vals['pagum_to'] = Edate1
                        vals['is_pagum_to'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_to'] = Edate1
                        vals['pagum_to'] = None
                        vals['is_pagum_to'] = True
        except:
            pass
        try:
                       
            if vals['date_from'] is not None:
                date_str = vals['date_from']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                _logger.info("######     ############# %s",Edate)
                _logger.info("######     ############# %s",type(Edate))


                if type(Edate) ==   str:
                    vals['ethiopian_from'] = None
                    vals['is_pagum_from'] = False
                    vals['pagum_from'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_from'] = Edate
                    vals['is_pagum_from'] = True
                    vals['pagum_from'] = ' '
        except:
            pass
        try:
            if vals['date_to'] is not None:
                
                date_str = vals['date_to']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate) ==   str:
                    vals['ethiopian_to'] = None
                    vals['is_pagum_to'] = False
                    vals['pagum_to'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_to'] = Edate
                    vals['is_pagum_to'] = True
                    vals['pagum_to'] = ' '
        except:
            pass
        return super(FiscalYear, self).write(vals)


    def action_reload_page(self):
        _logger.info("^^called^^")
     
        return {
                # 'type': 'ir.actions.act_url',
                # 'url': '/my/reload/',
                # 'target': 'new',
                # 'res_id': self.id,


                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    """
        This date convert and set function converts and sets dates.

        takes the date value and  the widget type from javascript

        then append on global variables pick1, pick2, pick3, and pick 4 as the picked  widget type



        When in edit mode, the method will automatically set the selected Ethiopian date, convert it to Gregorian, and save it.
        
    """
    @api.model
    def initial_date(self, data):
        _logger.info("################# Initial DATA %s", data)

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        if len(id[0]) <= 0:
            _logger.info("################# not fund")
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
            _logger.info("################# d: %s",date)

            return {'from': date, 'to': date}
        else:
            
            models = mm[0]
            search = self.env[models].search([('id','=',id[0])])
            if search.ethiopian_from != False and search.pagum_from == False and search.ethiopian_to != False and search.pagum_to == False:
                _logger.info("################# Both T")
                return {'from': search.ethiopian_from, 'to': search.ethiopian_to}
            elif search.ethiopian_from == False and search.pagum_from != False and search.ethiopian_to == False and search.pagum_to != False:
                _logger.info("################# Both T")
                date_from_str = str(search.pagum_from).split('/')
                date_to_str = str(search.pagum_to).split('/')
                date_from = date_from_str[2]+'-'+ date_from_str[0]+'-'+ date_from_str[1]
                date_to = date_to_str[2]+'-'+date_to_str[0]+'-'+date_to_str[1]
                return {'from': date_from, 'to': date_to}
            elif search.ethiopian_from == False and search.pagum_from == False and search.ethiopian_to != False and search.pagum_to == False:
                _logger.info("################# From - f  To - true")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': today, 'to': search.ethiopian_to}
            elif search.ethiopian_from == False and search.pagum_from == False and search.ethiopian_to == False and search.pagum_to != False:
                _logger.info("################# From - f  To - true")
                date_to_str = str(search.pagum_to).split('/')
                date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': today, 'to': date_to}
            elif search.ethiopian_from != False and search.pagum_from == False and search.ethiopian_to == False and search.pagum_to != False:
                _logger.info("################# From - f  To - true p")
                date_to_str = str(search.pagum_to).split('/')
                date_to = date_to_str[2]+'-'+date_to_str[0]+'-'+date_to_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': search.ethiopian_from, 'to': date_to}
            elif search.ethiopian_from !=  False and search.pagum_from == False and search.ethiopian_to == False and search.pagum_to == False:
                _logger.info("################# From - true  To - false")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': search.ethiopian_from, 'to': today}
            elif search.ethiopian_from ==  False and search.pagum_from != False and search.ethiopian_to == False and search.pagum_to == False:
                _logger.info("################# From - true  To - false")
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2]+'-'+date_from_str[0]+'-'+date_from_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': date_from, 'to': today}
            elif search.ethiopian_from ==  False and search.pagum_from != False and search.ethiopian_to != False and search.pagum_to == False:
                _logger.info("################# From - true  To - false pa")
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2]+'-'+date_from_str[0]+'-'+date_from_str[1]
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': date_from, 'to': search.ethiopian_to}
            elif search.ethiopian_from ==  False and search.pagum_from == False and search.ethiopian_to ==  False and search.pagum_to == False:
                _logger.info("################# both- false")
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                return {'from': today, 'to': today}
            
            else:
                date = datetime.now()
                date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
                _logger.info("################# d: %s",date)

                return date
    
    
    @api.model
    def date_convert_and_set(self,picked_date):

        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date,time = str(datetime.now()).split(" ")
        _logger.info(str(date_gr) + " " + str(f"{time}"))
        dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
        # date = str(date_et) + " " + str(f"{time}")
        date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
        date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
        data = {
            'day':   picked_date['day'],
            'month': picked_date['month'],
            'year': picked_date['year'],
            'pick': picked_date['pick']
        }
        if picked_date['pick'] == 1:
            pick1.append(data)
        if picked_date['pick'] == 2:
            pick2.append(data)
        if picked_date['pick'] == 3:
            pick3.append(data)
        if picked_date['pick'] == 4:
            pick3.append(data)





class TimeFream(models.Model):
    _inherit = 'reconciliation.time.fream'


    """
    There are four date replacing fields in this category: 
    
    category #1, ethiopian_to, pagum_to, is_pagum_to; 
    
    category #2, ethiopian_from, pagum_from, is_pagum_from; and 
    
    category #3, ethiopian_three, pagum_three, is_pagum_three.

    category #4, ethiopian_four, pagum_four, is_pagum_four, 

For example, if you only have one date in your model, use one of the following categories:
In budget Transfer, I have one date field that I substituted with one of the categories (Category #1).
    
    """
    ethiopian_to = fields.Date(string="in ethiopian date")
    pagum_to = fields.Char(string="in ethiopian date")
    is_pagum_to = fields.Boolean(default='True',string="in ethiopian date")


    ethiopian_from = fields.Date(string="in ethiopian date")
    pagum_from = fields.Char(string="in ethiopian date")
    is_pagum_from = fields.Boolean(default='True')

    

    # ethiopian_three = fields.Date(string="in ethiopian date")
    # pagum_three = fields.Char(string="in ethiopian date")
    # is_pagum_three = fields.Boolean(default='True',string="in ethiopian date")
   
    
    
    # ethiopian_four = fields.Date(string="in ethiopian date")
    # pagum_four = fields.Char(string="in ethiopian date")
    # is_pagum_four = fields.Boolean(default='True')

   

    @api.model
    def create(self, vals):
        _logger.info("vals:%s",vals)
        _logger.info("pick1:%s",pick1)
        _logger.info("pick2:%s",pick2)

        

        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                _logger.info("^^^^^^^^^^^ %s",type(Edate1))
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['date_from'] = date1
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False

                        pick1.clear()
                    if type(Edate1) ==   date:
                        vals['date_from'] = date1
                        vals['ethiopian_from'] = Edate1
                        pick1.clear()
                
        for i in range(0, len(pick2)):
        
            if i == (len(pick2)-1):
                date2 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
                Edate2 = EthiopianDateConverter.to_ethiopian(date2.year,date2.month,date2.day)
                _logger.info("^^^^^^^^^^^ %s",type(Edate2))

                if pick2[i]['pick'] == 2:
                    if type(Edate2) ==   str:
                        vals['ethiopian_to'] = None
                        vals['date_to'] = date2
                        vals['pagum_to'] = Edate2
                        vals['is_pagum_to'] = False

                        pick2.clear()
                    if type(Edate2) ==   date:
                        vals['date_to'] = date2
                        vals['ethiopian_to'] = Edate2
                        pick2.clear()
        try:
            if vals['date_from'] is not None and vals['date_to'] is not None:
                date1 = vals['date_from']
                date2 = vals['date_to']
                date_time_obj = date1.split('-')
                date_time_obj2 = date2.split('-')

                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate2 = EthiopianDateConverter.to_ethiopian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
                _logger.info("^^^^^^^^^^^ %s",type(Edate1))
                _logger.info("^^^^^^^^^^^ %s",type(Edate2))
                if type(Edate1) ==   date and type(Edate2) ==   date:
                    vals['ethiopian_from'] = Edate1
                    vals['ethiopian_to'] = Edate2
                elif type(Edate1) == date and type(Edate2) == str:
                    vals['ethiopian_from'] = Edate1
                    vals['pagum_to'] = Edate2
                    vals['is_pagum_to'] = False

                elif type(Edate1) ==   str and type(Edate2) ==   date:
                    vals['pagum_from'] = Edate1
                    vals['ethiopian_to'] = Edate2
                    vals['is_pagum_from'] = False

                elif type(Edate1) ==   str and type(Edate2) ==   str:
                    vals['pagum_from'] = Edate1
                    vals['pagum_to'] = Edate2
                    vals['is_pagum_from'] = False
                    vals['is_pagum_to'] = False

                else:
                    pass
        except:
            pass
        return super(TimeFream, self).create(vals)

    def write(self, vals):
        _logger.info("############# Write:%s",vals)
        try:
            if vals['ethiopian_from'] is not None:
                date_str = vals['ethiopian_from']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date_from'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_from'] = None
                        vals['pagum_from'] = Edate1
                        vals['is_pagum_from'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_from'] = Edate1
                        vals['pagum_from'] = None
                        vals['is_pagum_from'] = True
        except:
            pass
        try:

            if vals['ethiopian_to'] is not None:
                date_str = vals['ethiopian_to']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date_to'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_to'] = None
                        vals['pagum_to'] = Edate1
                        vals['is_pagum_to'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_to'] = Edate1
                        vals['pagum_to'] = None
                        vals['is_pagum_to'] = True
        except:
            pass
        try:
                       
            if vals['date_from'] is not None:
                date_str = vals['date_from']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                _logger.info("######     ############# %s",Edate)
                _logger.info("######     ############# %s",type(Edate))


                if type(Edate) ==   str:
                    vals['ethiopian_from'] = None
                    vals['is_pagum_from'] = False
                    vals['pagum_from'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_from'] = Edate
                    vals['is_pagum_from'] = True
                    vals['pagum_from'] = ' '
        except:
            pass
        try:
            if vals['date_to'] is not None:
                
                date_str = vals['date_to']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate) ==   str:
                    vals['ethiopian_to'] = None
                    vals['is_pagum_to'] = False
                    vals['pagum_to'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_to'] = Edate
                    vals['is_pagum_to'] = True
                    vals['pagum_to'] = ' '
        except:
            pass
        return super(TimeFream, self).write(vals)


    @api.model
    def initial_date(self, data):
        _logger.info("################# Initial DATA %s", data)

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        if len(id[0]) <= 0:
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
            return {'from': date, 'to': date}
        else:
            
            models = mm[0]
            search = self.env[models].search([('id','=',id[0])])
            From = []
            to = []
            three = []
            four = []

            # For initial date to widget One
            if search.ethiopian_from != False and search.pagum_from == False:
                From.append(search.ethiopian_from)
            if search.ethiopian_from == False and search.pagum_from != False:
                date_from_str = str(search.pagum_from).split('/')
                date_from = date_from_str[2]+'-'+date_from_str[0]+'-'+date_from_str[1]
                From.append(date_from)
            if search.ethiopian_from == False and search.pagum_from == False:
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                From.append(today)

            # For initial date to widget Two
            if search.ethiopian_to != False and search.pagum_to == False:
                to.append(search.ethiopian_to)
            if search.ethiopian_to == False and search.pagum_to != False:
                date_to_str = str(search.pagum_to).split('/')
                date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
                to.append(date_to)
            if search.ethiopian_to == False and search.pagum_to == False:
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                to.append(today)

            # # For initial date to widget Three

            # if search.ethiopian_three != False and search.pagum_three == False:
            #     three.append(search.ethiopian_three)
            # if search.ethiopian_three == False and search.pagum_three != False:
            #     date_to_str = str(search.pagum_three).split('/')
            #     date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
            #     three.append(date_to)
            # if search.ethiopian_three == False and search.pagum_three == False:
            #     today = datetime.now()
            #     today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
            #     three.append(today)

            # # For initial date to widget Four

            # if search.ethiopian_four != False and search.pagum_four == False:
            #     four.append(search.ethiopian_four)
            # if search.ethiopian_four == False and search.pagum_four != False:
            #     date_to_str = str(search.pagum_four).split('/')
            #     date_to = date_to_str[2] +'-'+date_to_str[0]+'-'+date_to_str[1]
            #     four.append(date_to)
            # if search.ethiopian_four == False and search.pagum_four == False:
            #     today = datetime.now()
            #     today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
            #     four.append(today)

            try:
                data = {
                    'from': From[0],
                    'to': to[0],
                    # 'three': three[0],
                }
            except:
                   data = {
                    'from': From,
                    'to': to,
                    'three': three,
                }
            _logger.info("DDDDDDDDDDDDDDDDDDData %s",data)
           
            return data
    

    @api.model
    def date_convert_and_set(self,picked_date):
        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date,time = str(datetime.now()).split(" ")
        dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
        # date = str(date_et) + " " + str(f"{time}")
        date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
        date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
        data = {
            'day':   picked_date['day'],
            'month': picked_date['month'],
            'year': picked_date['year'],
            'pick': picked_date['pick']
        }
        if picked_date['pick'] == 1:
            pick1.append(data)
        if picked_date['pick'] == 2:
            pick2.append(data)
        if picked_date['pick'] == 3:
            pick3.append(data)
        if picked_date['pick'] == 4:
            pick3.append(data)




class BudgetPlanning(models.Model):
    _inherit = "budget.planning"


    ethiopian_three = fields.Date(string="in ethiopian date")
    pagum_three = fields.Char(string="in ethiopian date")
    is_pagum_three = fields.Boolean(default='True',string="in ethiopian date")
   
    
   

    @api.model
    def create(self, vals):
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    if type(Edate1) ==   str:
                        vals['ethiopian_three'] = None
                        vals['date'] = date1
                        vals['pagum_three'] = Edate1
                        vals['is_pagum_three'] = False

                        pick1.clear()
                    if type(Edate1) ==   date:
                        vals['date'] = date1
                        vals['ethiopian_three'] = Edate1
                        pick1.clear()
        try:
            if vals['date'] is not None:
                date1 = vals['date']
                date_time_obj = date1.split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate1) ==   date:
                    vals['ethiopian_three'] = Edate1
                elif type(Edate1) ==   str :
                    vals['pagum_three'] = Edate1
                    vals['is_pagum_three'] = False

                else:
                    pass
        except:
            pass
        return super(BudgetPlanning, self).create(vals)
    


    def write(self, vals):
        _logger.info("############# Write:%s",vals)
        try:
            if vals['ethiopian_three'] is not None:
                date_str = vals['ethiopian_three']
                date_time_obj = date_str.split('-')
                date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                vals['date'] = date_gr
                if type(Edate1) ==   str:
                        vals['ethiopian_three'] = None
                        vals['pagum_three'] = Edate1
                        vals['is_pagum_three'] = False
                if type(Edate1) ==   date:
                        vals['ethiopian_three'] = Edate1
                        vals['pagum_three'] = None
                        vals['is_pagum_three'] = True

        except:
            pass
        try:           
            if vals['date'] is not None:
                date_str = vals['date']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                if type(Edate) == str:
                    vals['ethiopian_three'] = None
                    vals['is_pagum_three'] = False
                    vals['pagum_three'] = Edate
                elif type(Edate) == date:
                    vals['ethiopian_three'] = Edate
                    vals['is_pagum_three'] = True
                    vals['pagum_three'] = ' '
        except:
            pass
        return super(BudgetPlanning, self).write(vals)
    


    @api.model
    def initial_date(self, data):
        _logger.info("################# Initial DATA %s", data)

        dd = data['url'].split('id=')
        id = str(dd[1]).split('&')
        m = data['url'].split('model=')
        mm = m[1].split('&')
        if len(id[0]) <= 0:
            date = datetime.now()
            date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
            return {'from': date, 'to': date}
        else:
            
            models = mm[0]
            search = self.env[models].search([('id','=',id[0])])
            three = []

            # For initial date to widget One
            if search.ethiopian_three != False and search.pagum_three == False:
                three.append(search.ethiopian_three)
            if search.ethiopian_three == False and search.pagum_three != False:
                date_from_str = str(search.pagum_three).split('/')
                date_from = date_from_str[2]+'-'+date_from_str[0]+'-'+date_from_str[1]
                three.append(date_from)
            if search.ethiopian_three == False and search.pagum_three == False:
                today = datetime.now()
                today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
                three.append(today)
            data = {
                'three': three[0]
            }
            _logger.info("Dddddddddddddddddddddddd %s",data)
            return data
            
    @api.model
    def date_convert_and_set(self,picked_date):
        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date,time = str(datetime.now()).split(" ")
        dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
        # date = str(date_et) + " " + str(f"{time}")
        date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
        date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
        data = {
            'day':   picked_date['day'],
            'month': picked_date['month'],
            'year': picked_date['year'],
            'pick': picked_date['pick']
        }
        if picked_date['pick'] == 1:
            pick1.append(data)
        if picked_date['pick'] == 2:
            pick2.append(data)
        if picked_date['pick'] == 3:
            pick3.append(data)
        if picked_date['pick'] == 4:
            pick3.append(data)




# class BudgetTransfer(models.Model):
    # _inherit = "budget.transfer"

    # ethiopian_from = fields.Date(string="in ethiopian date")
    # pagum_from = fields.Char(string="in ethiopian date")
    # is_pagum_from = fields.Boolean(default='True')

   

    # @api.model
    # def create(self, vals):
    #     for i in range(0, len(pick1)):
  
    #         if i == (len(pick1)-1):
    #             date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
    #             Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
    #             if pick1[i]['pick'] == 1:
    #                 if type(Edate1) ==   str:
    #                     vals['ethiopian_from'] = None
    #                     vals['date'] = date1
    #                     vals['pagum_from'] = Edate1
    #                     vals['is_pagum_from'] = False

    #                     pick1.clear()
    #                 if type(Edate1) ==   date:
    #                     vals['date'] = date1
    #                     vals['ethiopian_from'] = Edate1
    #                     pick1.clear()
    #             vals['squ'] = self.env['ir.sequence'].next_by_code('budget.transfer') or _('New')
                
    #             date_1 = str(date1)
    #             date_1 = date_1.split('-')
    #             vals['squ'] = "BT/"+date_1[0]+"/"+vals['squ']
    #             _logger.info("After :%s",vals['squ'])
    #             vals['name'] = vals['squ']
    #             # The blow code used for only budget transfer moduel

    #             active_time_frame = self.env['reconciliation.time.fream'].search(
    #                 [('date_from', '<=', date1), ('date_to', '>=', date1)], limit=1)
    #             vals['time_frame'] = active_time_frame.id
    #             vals['fiscal_year'] = active_time_frame.fiscal_year.id


    #     try:
    #         if vals['date'] is not None:
    #             date1 = vals['date']
    #             date_time_obj = date1.split('-')
    #             Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #             if type(Edate1) ==   date:
    #                 vals['ethiopian_from'] = Edate1
    #             elif type(Edate1) ==   str :
    #                 vals['pagum_from'] = Edate1
    #                 vals['is_pagum_from'] = False

    #             else:
    #                 pass
    #             vals['squ'] = self.env['ir.sequence'].next_by_code('budget.transfer') or _('New')

    #             date_1 = str(date1)
    #             date_1 = date_1.split('-')
    #             vals['squ'] = "BT/"+date_1[0]+"/"+vals['squ']
    #             _logger.info("After :%s",vals['squ'])
    #             vals['name'] = vals['squ']
    #             active_time_frame = self.env['reconciliation.time.fream'].search(
    #                 [('date_from', '<=', date1), ('date_to', '>=', date1)], limit=1)
    #             vals['time_frame'] = active_time_frame.id
    #             vals['fiscal_year'] = active_time_frame.fiscal_year.id


    #     except:
    #         pass

    #     return super(BudgetTransfer, self).create(vals)
    


    # def write(self, vals):
    #     _logger.info("############# Write:%s",vals)
    #     try:
    #         if vals['ethiopian_from'] is not None:
    #             date_str = vals['ethiopian_from']
    #             date_time_obj = date_str.split('-')
    #             date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #             Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
    #             vals['date'] = date_gr
    #             if type(Edate1) ==   str:
    #                     vals['ethiopian_from'] = None
    #                     vals['pagum_from'] = Edate1
    #                     vals['is_pagum_from'] = False
    #             if type(Edate1) ==   date:
    #                     vals['ethiopian_from'] = Edate1
    #                     vals['pagum_from'] = None
    #                     vals['is_pagum_from'] = True

    #             # The blow code used for only budget transfer moduel

    #             active_time_frame = self.env['reconciliation.time.fream'].search(
    #                 [('date_from', '<=', vals['date']), ('date_to', '>=', vals['date'])], limit=1)
    #             if not active_time_frame.id:
    #                 pass
    #             else:
    #                 self['time_frame'] = active_time_frame
    #                 self['fiscal_year'] = active_time_frame.fiscal_year.id
    #     except:
    #         pass
    #     try:           
    #         if vals['date'] is not None:
    #             date_str = vals['date']
    #             date_time_obj = date_str.split('-')
    #             Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #             if type(Edate) == str:
    #                 vals['ethiopian_from'] = None
    #                 vals['is_pagum_from'] = False
    #                 vals['pagum_from'] = Edate
    #             elif type(Edate) == date:
    #                 vals['ethiopian_from'] = Edate
    #                 vals['is_pagum_from'] = True
    #                 vals['pagum_from'] = ' '
    #     except:
    #         pass
    #     return super(BudgetTransfer, self).write(vals)
    


    # @api.model
    # def date_convert_and_set(self,picked_date):
    #     date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
    #     date,time = str(datetime.now()).split(" ")
    #     dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
    #     # date = str(date_et) + " " + str(f"{time}")
    #     date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
    #     date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
    #     data = {
    #         'day':   picked_date['day'],
    #         'month': picked_date['month'],
    #         'year': picked_date['year'],
    #         'pick': picked_date['pick']
    #     }
    #     if picked_date['pick'] == 1:
    #         pick1.append(data)
    #     if picked_date['pick'] == 2:
    #         pick2.append(data)
    #     if picked_date['pick'] == 3:
    #         pick3.append(data)
    #     if picked_date['pick'] == 4:
    #         pick3.append(data)



