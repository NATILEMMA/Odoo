
# import random
# import string
# import werkzeug.urls
# from odoo import tools
# from collections import defaultdict
# from datetime import datetime, date 
# from odoo import api, exceptions, fields, models, _
# from ethiopian_date import EthiopianDateConverter
# import logging
# _logger = logging.getLogger(__name__)
# pick1 = []
# pick2 = []
# pick3 = []
# pick4 = []

# class ResUsers(models.Model):
#     _inherit = 'res.users'


#     is_ethiopian_datepicker = fields.Boolean(string="Ethiopian Datepicker")

#     def transfer_node_to_modifiers(node, modifiers, context=None, in_tree_view=False):
#         if node.get('attrs'):
#             #If you want, add more conditions here
#             if ', uid' in  node.get('attrs'):
#                 user_id = str(context.get('uid', 1))
#                 user_id = ', ' + user_id
#                 attrs = node.get('attrs')
#                 attrs = attrs.replace(', uid', user_id)
#                 node.set('attrs', attrs)
#             modifiers.update(eval(node.get('attrs')))

#         if node.get('states'):
#             if 'invisible' in modifiers and isinstance(modifiers['invisible'], list):
#                 # TODO combine with AND or OR, use implicit AND for now.
#                 modifiers['invisible'].append(('state', 'not in', node.get('states').split(',')))
#             else:
#                 modifiers['invisible'] = [('state', 'not in', node.get('states').split(','))]

#         for a in ('invisible', 'readonly', 'required'):
#             if node.get(a):
#                 v = bool(eval(node.get(a), {'context': context or {}}))
#                 if in_tree_view and a == 'invisible':
#                     # Invisible in a tree view has a specific meaning, make it a
#                     # new key in the modifiers attribute.
#                     modifiers['tree_invisible'] = v
#                 elif v or (a not in modifiers or not isinstance(modifiers[a], list)):
#                     # Don't set the attribute to False if a dynamic value was
#                     # provided (i.e. a domain from attrs or states).
#                     modifiers[a] = v

#     @api.model
#     def initial_date(self, data):
#             return False
           
    

#     @api.onchange('is_ethiopian_datepicker')
#     def onchange_ethiopiandatepicker(self):
#         """ 
#                     Duplicate Only The SQL Query and replace your model name

#         """
#         if self.is_ethiopian_datepicker == True:
#             query = """
#                 update  reconciliation_time_fream  set  is_ethiopian_datepicker=%s where id=id
#             """ %(True)
            

#             cr = self._cr
#             # cr.execute(query)
#             ethio_groups = self.env['res.groups'].search([('name','=','Ethiopian Datepicker')], limit=1)
#             gro_groups = self.env['res.groups'].search([('name','=','Gregory Datepicker')], limit=1)
#             ethio_user_list = []
#             gro_user_list = []

#             _logger.info(" ###### ethio_groups %s",ethio_groups.users)
#             _logger.info(" ###### gro_groups %s",gro_groups.users)

#             if ethio_groups.users is not None:
#                 if self.env.user in ethio_groups.users: 
#                     for user in gro_groups.users:
#                         if self.env.user.id == user.id:
#                             pass
#                         else:
#                             gro_user_list.append(user.id)
#                     for users in ethio_groups.users:
#                         ethio_user_list.append(users.id)
#                 else:
#                     for users in ethio_groups.users:
#                         ethio_user_list.append(users.id)
#                     for user in gro_groups.users:
#                         _logger.info(" ###### gro_groups %s",user.name)

#                         if self.env.user.id == user.id:
#                             _logger.info(" ###### TTT %s",user.name)

#                             pass
#                         else:
#                             _logger.info(" ###### FF %s",user.name)

#                             gro_user_list.append(user.id)
#                     ethio_user_list.append(self.env.user.id)

#                 _logger.info(" ###### ethio_user_list %s",ethio_user_list)
#                 _logger.info(" ###### gro_user_list %s",gro_user_list)
                
#                 ethio_groups['users'] = [(6,0,ethio_user_list)]
#                 gro_groups['users'] = [(6,0,gro_user_list)]
            
#             else:
#                 pass


#             self.is_ethiopian_datepicker = True

     
#         if self.is_ethiopian_datepicker == False:
#             query = """
#                 update  reconciliation_time_fream  set is_ethiopian_datepicker = %s where id=id
#             """ %(False)

#             cr = self._cr
#             # cr.execute(query)
#             ethio_groups = self.env['res.groups'].search([('name','=','Ethiopian Datepicker')], limit=1)
#             gro_groups = self.env['res.groups'].search([('name','=','Gregory Datepicker')], limit=1)
#             ethio_user_list = []
#             gro_user_list = []
#             if gro_groups.users is not None:
           

                
#                 if self.env.user in gro_groups.users: 
#                     for user in ethio_groups.users:
#                         if self.env.user.id == user.id:
#                             pass
#                         else:
#                             ethio_user_list.append(user.id)
#                     for users in gro_groups.users:
#                         gro_user_list.append(users.id)
#                 else:
#                     for users in gro_groups.users:
#                         gro_user_list.append(users.id)
#                     for user in ethio_groups.users:
#                         _logger.info(" ###### gro_groups %s",user.name)

#                         if self.env.user.id == user.id:
#                             _logger.info(" ###### TTT %s",user.name)

#                             pass
#                         else:
#                             _logger.info(" ###### FF %s",user.name)

#                             ethio_user_list.append(user.id)
#                     gro_user_list.append(self.env.user.id)

#                 _logger.info(" ###### ethio_user_list %s",ethio_user_list)
#                 _logger.info(" ###### gro_user_list %s",gro_user_list)
                
#                 ethio_groups['users'] = [(6,0,ethio_user_list)]
#                 gro_groups['users'] = [(6,0,gro_user_list)]
            

#                 # if self.env.user in gro_groups.users: 
#                 #     for user in ethio_groups.users:
#                 #         if self.env.user.id == user.id:
#                 #             pass
#                 #         else:
#                 #             ethio_user_list.append(user.id)
#                 #     for users in gro_groups.users:
#                 #         gro_user_list.append(users.id)
#                 # else:
#                 #     _logger.info("Nnnnnnnnnnnnn in gre")
#                 #     for user_e in ethio_groups.users:
#                 #         _logger.info("^^^^^^^^^^^^ %s",user_e.name)
#                 #         if self.env.user.id == user_e.id:
#                 #             pass
#                 #         else:
#                 #             ethio_user_list.append(user_e.id)
#                 #     for users in gro_groups.users:
#                 #         gro_user_list.append(users.id)
                    
#                 #     gro_user_list.append(self.env.user.id)
#                 # _logger.info("gro_user_list in gre %s",gro_user_list)
#                 # _logger.info("ethio_user_list in gre %s",ethio_user_list)

              

#                 # ethio_groups['users'] = [(6,0,ethio_user_list)]
#                 # gro_groups['users'] = [(6,0,gro_user_list)]
#             else:
#                 pass

#             self.is_ethiopian_datepicker = False



# class ResConfigSettings(models.TransientModel):

#     _inherit = "res.config.settings"

#     is_ethiopian_datepicker = fields.Boolean("Ethiopian Datepicker")
   


   
#     def set_values(self):
#         _logger.info("############################## %s",self.is_ethiopian_datepicker)
#         res = super(ResConfigSettings, self).set_values()
#         self.env['ir.config_parameter'].set_param('EthiopianCalendar.is_ethiopian_datepicker', self.is_ethiopian_datepicker)
#         return res

#     @api.onchange('is_ethiopian_datepicker')
#     def onchange_ethiopiandatepicker(self):
#         """ 
#                     Duplicate Only The SQL Query and replace your model name

#         """

#         # tools.drop_view_if_exists(self._cr, 'reconciliation_time_fream')
#         if self.is_ethiopian_datepicker == True:
#             query = """
#                 update  reconciliation_time_fream  set ticked_user	= %s  where id=id
#             """ %(self.env.user.id)

#             cr = self._cr
#             cr.execute(query)

#             users = self.env['res.partner'].search([('user_id','=',self.env.user.id)], limit=1)
#             _logger.info("############## %s",users)
#             _logger.info("############## %s", users.ticked_user)

#             # users = users.ticked_user
#             # line_value_2.account_ids = [(6,0,values)]
#             # self.env.cr.commit()
#         if self.is_ethiopian_datepicker == False:
#             query = """
#                 update  reconciliation_time_fream  set is_ethiopian_datepicker	= %s  where id=id
#             """ %(False)

#             cr = self._cr
#             cr.execute(query)
#             self.is_ethiopian_datepicker = False
#             # self.env.cr.commit()


        

    
# class FiscalYear(models.Model):
#     _inherit = 'fiscal.year'

#     """ 
#     """

#     ethiopian_to = fields.Date(string="in ethiopian date")
#     ethiopian_from = fields.Date(string="in ethiopian date")
#     pagum_from = fields.Char(string="in ethiopian date")
#     pagum_to = fields.Char(string="in ethiopian date")
#     is_pagum_from = fields.Boolean(default='True')
#     is_pagum_to = fields.Boolean(default='True',string="in ethiopian date")
 
    
#     @api.model
#     def create(self, vals):

#         """
#             Use this for loop to get your most recently selected date from the global append Ethiopian date.

#             if your widget type are

#             - ethiopian_calander_widget user pick1
#             - ethiopian_calander_widget_two user pick2
#             - ethiopian_calander_widget_three user pick3
#             - ethiopian_calander_widget_four user pick4
           
#        Pick1 is used in the for loop below because my view displays an Ethiopian date picker using the *ethiopian_calander_widget* widget type.

#         """
#         for i in range(0, len(pick1)):
  
#             if i == (len(pick1)-1):
#                 date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
#                 Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
#                 _logger.info("^^^^^^^^^^^ %s",type(Edate1))
#                 if pick1[i]['pick'] == 1:
#                     if type(Edate1) ==   str:
#                         vals['ethiopian_from'] = None
#                         vals['date_from'] = date1
#                         vals['pagum_from'] = Edate1
#                         vals['is_pagum_from'] = False

#                         pick1.clear()
#                     if type(Edate1) ==   date:
#                         vals['date_from'] = date1
#                         vals['ethiopian_from'] = Edate1
#                         pick1.clear()
                
#         for i in range(0, len(pick2)):
        
#             if i == (len(pick2)-1):
#                 date2 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
#                 Edate2 = EthiopianDateConverter.to_ethiopian(date2.year,date2.month,date2.day)
#                 _logger.info("^^^^^^^^^^^ %s",type(Edate2))

#                 if pick2[i]['pick'] == 2:
#                     if type(Edate2) ==   str:
#                         vals['ethiopian_to'] = None
#                         vals['date_to'] = date2
#                         vals['pagum_to'] = Edate2
#                         vals['is_pagum_to'] = False

#                         pick2.clear()
#                     if type(Edate2) ==   date:
#                         vals['date_to'] = date2
#                         vals['ethiopian_to'] = Edate2
#                         pick2.clear()
#         try:
#             if vals['date_from'] is not None and vals['date_to'] is not None:
#                 date1 = vals['date_from']
#                 date2 = vals['date_to']
#                 date_time_obj = date1.split('-')
#                 date_time_obj2 = date2.split('-')

#                 Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 Edate2 = EthiopianDateConverter.to_ethiopian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
#                 _logger.info("^^^^^^^^^^^ %s",type(Edate1))
#                 _logger.info("^^^^^^^^^^^ %s",type(Edate2))
#                 if type(Edate1) ==   date and type(Edate2) ==   date:
#                     vals['ethiopian_from'] = Edate1
#                     vals['ethiopian_to'] = Edate2
#                 elif type(Edate1) == date and type(Edate2) == str:
#                     vals['ethiopian_from'] = Edate1
#                     vals['pagum_to'] = Edate2
#                     vals['is_pagum_to'] = False

#                 elif type(Edate1) ==   str and type(Edate2) ==   date:
#                     vals['pagum_from'] = Edate1
#                     vals['ethiopian_to'] = Edate2
#                     vals['is_pagum_from'] = False

#                 elif type(Edate1) ==   str and type(Edate2) ==   str:
#                     vals['pagum_from'] = Edate1
#                     vals['pagum_to'] = Edate2
#                     vals['is_pagum_from'] = False
#                     vals['is_pagum_to'] = False

#                 else:
#                     pass
#         except:
#             pass
       
#         return super(FiscalYear, self).create(vals)


    
#     def write(self, vals):
#         _logger.info("########dd##### Write:%s",vals)
        
#         """
#             This try-catch method is used to convert the Gregorian calendar to the Ethiopian calendar.
        
#         """
#         try:
#             if vals['date_from'] is not None:
#                 date_str = vals['date_from']
#                 date_time_obj = date_str.split('-')
#                 Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 if type(Edate) ==   str:
#                     vals['ethiopian_from'] = None
#                     vals['is_pagum_from'] = False
#                     vals['pagum_from'] = Edate
#                 elif type(Edate) == date:
#                     vals['ethiopian_from'] = Edate
#                     vals['is_pagum_from'] = True
#                     vals['pagum_from'] = ' '
              
#         except:
#             pass
#         try:
#             if vals['date_to'] is not None:
#                 date_str = vals['date_to']
#                 date_time_obj = date_str.split('-')
#                 Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 if type(Edate) ==   str:
#                     vals['ethiopian_to'] = None
#                     vals['is_pagum_to'] = False
#                     vals['pagum_to'] = Edate
#                 elif type(Edate) == date:
#                     vals['ethiopian_to'] = Edate
#                     vals['is_pagum_to'] = True
#                     vals['pagum_to'] = ' '
              
#         except:
#             pass
       
       
#         # self.action_reload_page()
#         return super(FiscalYear, self).write(vals)


#     def action_reload_page(self):
#         _logger.info("^^called^^")
     
#         return {
#                 # 'type': 'ir.actions.act_url',
#                 # 'url': '/my/reload/',
#                 # 'target': 'new',
#                 # 'res_id': self.id,


#                 'type': 'ir.actions.client',
#                 'tag': 'reload',
#             }

#     """
#         This date convert and set function converts and sets dates.

#         takes the date value and  the widget type from javascript

#         then append on global variables pick1, pick2, pick3, and pick 4 as the picked  widget type



#         When in edit mode, the method will automatically set the selected Ethiopian date, convert it to Gregorian, and save it.
        
#     """
#     @api.model
#     def initial_date(self, data):
#         _logger.info("################# Initial DATA %s", data)

#         dd = data['url'].split('id=')
#         id = str(dd[1]).split('&')
#         m = data['url'].split('model=')
#         mm = m[1].split('&')
#         if len(id[0]) <= 0:
#             _logger.info("################# not fund")
#             date = datetime.now()
#             date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
#             _logger.info("################# d: %s",date)

#             return {'from': date, 'to': date}
#         else:
            
#             models = mm[0]
#             search = self.env[models].search([('id','=',id[0])])
#             _logger.info("################# From Date %s", search.ethiopian_from)
#             _logger.info("################# From Date %s", search.ethiopian_to)

#             if search.ethiopian_from is not None and search.ethiopian_to is not None:
#                 _logger.info("################# Both T")

#                 return {'from': search.ethiopian_from, 'to': search.ethiopian_to}
#             elif search.ethiopian_from is None and search.ethiopian_to is not None:
#                 _logger.info("################# From - f  To - true")

#                 today = datetime.now()
#                 today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
#                 return {'from': today, 'to': search.ethiopian_to}
#             elif search.ethiopian_from is  None and search.ethiopian_to is not None:
#                 _logger.info("################# From - true  To - false")
                            
#                 today = datetime.now()
#                 today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
#                 return {'from': today, 'to': search.ethiopian_to}
#             elif search.ethiopian_from is  None and search.ethiopian_to is  None:
#                 _logger.info("################# both- false")
                            
#                 today = datetime.now()
#                 today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
#                 return {'from': today, 'to': today}
            
#             else:
#                 date = datetime.now()
#                 date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
#                 _logger.info("################# d: %s",date)

#                 return date
#     @api.model
#     def date_convert_and_set(self,picked_date):
#         try:
#             dd = picked_date['url'].split('id=')
#             id = str(dd[1]).split('&')
#             m = picked_date['url'].split('model=')
#             mm = m[1].split('&')
#             if len(id[0]) <= 0:
#                 _logger.info("not fund")

#             else:
#                     _logger.info("lol")
#                     models = mm[0]
#                     search = self.env[models].search([('id','=',id[0])])
#                     date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
#                     date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
#                     if models == "fiscal.year":
#                         if picked_date['pick'] == 1:
#                             if int(picked_date['month']) == 13:
#                                 search.update({
#                                 'date_from': date_gr,
#                                 'pagum_from': date,
#                                 'is_pagum_from': False,
#                                 'ethiopian_from': None
#                                 })
#                                 search.action_reload_page()
#                             elif int(picked_date['month']) == 2 and int(picked_date['day']) > 28:
#                                 search.update({
#                                 'date_from': date_gr,
#                                 'pagum_from': date,
#                                 'is_pagum_from': False,
#                                 'ethiopian_from': None

#                                 })
#                                 search.action_reload_page()
#                             else:
#                                 search.update({
#                                 'date_from': date_gr,
#                                 'ethiopian_from': date,
#                                 'is_pagum_from': True,
#                                 'pagum_from': " "

#                                 })
#                                 search.action_reload_page()
                            
#                             # return {
#                             #         'type': 'ir.actions.client',
#                             #         'tag': 'reload',
#                             #     }
#                             # self.env.cr.commit()
#                             # return search
#                             search.action_reload_page()
                            

#                         if picked_date['pick'] == 2:
#                             if int(picked_date['month']) == 13:

#                                 search.write({
#                                     'date_to': date_gr,
#                                     'pagum_to':date, 
#                                     'is_pagum_to': False,
#                                     'ethiopian_to': None
#                                     })
#                             elif int(picked_date['month']) == 2 and int(picked_date['day']) > 28:
#                                 search.write({
#                                 'date_to': date_gr,
#                                 'pagum_to': date,
#                                 'is_pagum_to': False,
#                                 'ethiopian_to': None

#                                 })
#                                 search.action_reload_page()
#                             else:
#                                 search.write({
#                                     'date_to': date_gr,
#                                     'ethiopian_to':date,
#                                     'is_pagum_to': True,
#                                     'pagum_to': " "


#                                     })
#                             # return {
#                             #         'type': 'ir.actions.client',
#                             #         'tag': 'reload',
#                             #     }
#                             # self.env.cr.commit()
#                             # return search 
#                             search.action_reload_page()
                    
#                     return {
#                         'type': 'ir.actions.client',
#                         'tag': 'reload',
#                     }
                    
       

#         except:
#             pass
#         date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
#         date,time = str(datetime.now()).split(" ")
#         _logger.info(str(date_gr) + " " + str(f"{time}"))
#         dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
#         # date = str(date_et) + " " + str(f"{time}")
#         date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
#         date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
#         data = {
#             'day':   picked_date['day'],
#             'month': picked_date['month'],
#             'year': picked_date['year'],
#             'pick': picked_date['pick']
#         }
#         if picked_date['pick'] == 1:
#             pick1.append(data)
#         if picked_date['pick'] == 2:
#             pick2.append(data)
#         if picked_date['pick'] == 3:
#             pick3.append(data)
#         if picked_date['pick'] == 4:
#             pick3.append(data)





# class TimeFream(models.Model):
#     _inherit = 'reconciliation.time.fream'


#     ethiopian_to = fields.Date(string="in ethiopian date")
#     ethiopian_from = fields.Date(string="in ethiopian date")
#     pagum_from = fields.Char(string="in ethiopian date")
#     pagum_to = fields.Char(string="in ethiopian date")
#     is_pagum_from = fields.Boolean(default='True')
#     is_pagum_to = fields.Boolean(default='True',string="in ethiopian date")
#     # feb_et_from = fields.Char(string="Date From")
#     # feb_et_to = fields.Char(string="Date To")
#     # ticked_user = fields.Many2one('res.users', default= lambda self: self.env.session.user)
#     # is_ethiopian_datepicker = fields.Boolean(related='ticked_user.is_ethiopian_datepicker',
#     #                          string='Request', readonly=True,
#     #                          store=True)
    
   
#      # @api.depends()
#     def _get_current_user(self):
#         for rec in self:
#             rec.current_user = self.env.user
#         # i think this work too so you don't have to loop
#         self.update({'current_user' : self.env.user.id})
                        

#     # @api.depends('is_ethiopian_datepicker')
#     # def _compute_can_see(self):
#     #     _logger.info("############################### ")
#     #     _logger.info(self.ticked_user)
#     #     _logger.info(self.ticked_user.is_ethiopian_datepicker)

#     #     for rec in self:
#     #         rec.check = self.ticked_user.is_ethiopian_datepicker

        

  

#     @api.model
#     def create(self, vals):
#         _logger.info("convvvvvvvvvvvvvvvvvv ethio createeeeeeeeeeeee %s",vals)

#         for i in range(0, len(pick1)):
  
#             if i == (len(pick1)-1):
#                 date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
#                 Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
#                 _logger.info("^^^^^^^^^^^ %s",type(Edate1))
#                 if pick1[i]['pick'] == 1:
#                     if type(Edate1) ==   str:
#                         vals['ethiopian_from'] = None
#                         vals['date_from'] = date1
#                         vals['pagum_from'] = Edate1
#                         vals['is_pagum_from'] = False

#                         pick1.clear()
#                     if type(Edate1) ==   date:
#                         vals['date_from'] = date1
#                         vals['ethiopian_from'] = Edate1
#                         pick1.clear()
                
#         for i in range(0, len(pick2)):
        
#             if i == (len(pick2)-1):
#                 date2 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
#                 Edate2 = EthiopianDateConverter.to_ethiopian(date2.year,date2.month,date2.day)
#                 _logger.info("^^^^^^^^^^^ %s",type(Edate2))

#                 if pick2[i]['pick'] == 2:
#                     if type(Edate2) ==   str:
#                         vals['ethiopian_to'] = None
#                         vals['date_to'] = date2
#                         vals['pagum_to'] = Edate2
#                         vals['is_pagum_to'] = False

#                         pick2.clear()
#                     if type(Edate2) ==   date:
#                         vals['date_to'] = date2
#                         vals['ethiopian_to'] = Edate2
#                         pick2.clear()
#         try:

#             if vals['ethiopian_from'] is not None and vals['ethiopian_to'] is not None:
#                 date1 = vals['ethiopian_from']
#                 date2 = vals['ethiopian_to']
#                 date_time_obj = date1.split('-')
#                 date_time_obj2 = date2.split('-')

#                 date_gr_from = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 Edate1 = EthiopianDateConverter.to_ethiopian(date_gr_from.year,date_gr_from.month,date_gr_from.day)

#                 date_gr_to = EthiopianDateConverter.to_gregorian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
#                 Edate2 = EthiopianDateConverter.to_ethiopian(date_gr_to.year,date_gr_to.month,date_gr_to.day)


#                 _logger.info("^^^^^^^^^^^ %s",type(Edate1))
#                 _logger.info("^^^^^^^^^^^ %s",type(Edate2))
#                 vals['date_from'] = date_gr_from
#                 vals['date_to'] = date_gr_to
#                 if type(Edate1) ==   date and type(Edate2) ==   date:
#                     vals['ethiopian_from'] = Edate1
#                     vals['ethiopian_to'] = Edate2
#                 elif type(Edate1) == date and type(Edate2) == str:
#                     vals['ethiopian_from'] = Edate1
#                     vals['pagum_to'] = Edate2
#                     vals['is_pagum_to'] = False

#                 elif type(Edate1) ==   str and type(Edate2) ==   date:
#                     vals['pagum_from'] = Edate1
#                     vals['ethiopian_to'] = Edate2
#                     vals['is_pagum_from'] = False

#                 elif type(Edate1) ==   str and type(Edate2) ==   str:
#                     vals['pagum_from'] = Edate1
#                     vals['pagum_to'] = Edate2
#                     vals['is_pagum_from'] = False
#                     vals['is_pagum_to'] = False

#                 else:
#                     pass

                
#                 # vals['date_from'] = date_gr
#                 # if type(Edate1) ==   str:
#                 #         vals['ethiopian_from'] = None
#                 #         vals['pagum_from'] = Edate1
#                 #         vals['is_pagum_from'] = False
#                 # if type(Edate1) ==   date:
#                 #         vals['ethiopian_from'] = Edate1
#                 #         vals['pagum_from'] = None
#                 #         vals['is_pagum_from'] = True

#             if vals['date_from'] is not None and vals['date_to'] is not None:
#                 date1 = vals['date_from']
#                 date2 = vals['date_to']
#                 date_time_obj = date1.split('-')
#                 date_time_obj2 = date2.split('-')

#                 Edate1 = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 Edate2 = EthiopianDateConverter.to_ethiopian(int(date_time_obj2[0]),int(date_time_obj2[1]),int(date_time_obj2[2]))
#                 _logger.info("^^^^^^^^^^^ %s",type(Edate1))
#                 _logger.info("^^^^^^^^^^^ %s",type(Edate2))
#                 if type(Edate1) ==   date and type(Edate2) ==   date:
#                     vals['ethiopian_from'] = Edate1
#                     vals['ethiopian_to'] = Edate2
#                 elif type(Edate1) == date and type(Edate2) == str:
#                     vals['ethiopian_from'] = Edate1
#                     vals['pagum_to'] = Edate2
#                     vals['is_pagum_to'] = False

#                 elif type(Edate1) ==   str and type(Edate2) ==   date:
#                     vals['pagum_from'] = Edate1
#                     vals['ethiopian_to'] = Edate2
#                     vals['is_pagum_from'] = False

#                 elif type(Edate1) ==   str and type(Edate2) ==   str:
#                     vals['pagum_from'] = Edate1
#                     vals['pagum_to'] = Edate2
#                     vals['is_pagum_from'] = False
#                     vals['is_pagum_to'] = False

#                 else:
#                     pass
#         except:
#             pass
#         return super(TimeFream, self).create(vals)

#     def write(self, vals):
#         _logger.info("############# Write:%s",vals)
#         try:
#             if vals['ethiopian_from'] is not None:
#                 date_str = vals['ethiopian_from']
#                 date_time_obj = date_str.split('-')
#                 date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
#                 vals['date_from'] = date_gr
#                 if type(Edate1) ==   str:
#                         vals['ethiopian_from'] = None
#                         vals['pagum_from'] = Edate1
#                         vals['is_pagum_from'] = False
#                 if type(Edate1) ==   date:
#                         vals['ethiopian_from'] = Edate1
#                         vals['pagum_from'] = None
#                         vals['is_pagum_from'] = True

#             if vals['ethiopian_to'] is not None:
#                 date_str = vals['ethiopian_to']
#                 date_time_obj = date_str.split('-')
#                 date_gr = EthiopianDateConverter.to_gregorian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 Edate1 = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
#                 vals['date_to'] = date_gr
#                 if type(Edate1) ==   str:
#                         vals['ethiopian_to'] = None
#                         vals['pagum_to'] = Edate1
#                         vals['is_pagum_to'] = False
#                 if type(Edate1) ==   date:
#                         vals['ethiopian_to'] = Edate1
#                         vals['pagum_to'] = None
#                         vals['is_pagum_to'] = True
                       
#             if vals['date_from'] is not None:
#                 date_str = vals['date_from']
#                 date_time_obj = date_str.split('-')
#                 Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 _logger.info("######     ############# %s",Edate)
#                 _logger.info("######     ############# %s",type(Edate))


#                 if type(Edate) ==   str:
#                     vals['ethiopian_from'] = None
#                     vals['is_pagum_from'] = False
#                     vals['pagum_from'] = Edate
#                 elif type(Edate) == date:
#                     vals['ethiopian_from'] = Edate
#                     vals['is_pagum_from'] = True
#                     vals['pagum_from'] = ' '
#         except:
#             pass
#         try:
#             if vals['date_to'] is not None:
                
#                 date_str = vals['date_to']
#                 date_time_obj = date_str.split('-')
#                 Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 if type(Edate) ==   str:
#                     vals['ethiopian_to'] = None
#                     vals['is_pagum_to'] = False
#                     vals['pagum_to'] = Edate
#                 elif type(Edate) == date:
#                     vals['ethiopian_to'] = Edate
#                     vals['is_pagum_to'] = True
#                     vals['pagum_to'] = ' '
#         except:
#             pass
#         return super(TimeFream, self).write(vals)


#     @api.model
#     def initial_date(self, data):
#         _logger.info("################# Initial DATA %s", data)

#         dd = data['url'].split('id=')
#         id = str(dd[1]).split('&')
#         m = data['url'].split('model=')
#         mm = m[1].split('&')
#         if len(id[0]) <= 0:
#             _logger.info("################# not fund")
#             date = datetime.now()
#             date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
#             _logger.info("################# d: %s",date)

#             return {'from': date, 'to': date}
#         else:
            
#             models = mm[0]
#             search = self.env[models].search([('id','=',id[0])])
#             _logger.info("################# From Date %s", search.ethiopian_from)
#             _logger.info("################# From Date %s", search.ethiopian_to)

#             if search.ethiopian_from != False and search.ethiopian_to != False:
#                 _logger.info("################# Both T")

#                 return {'from': search.ethiopian_from, 'to': search.ethiopian_to}
#             elif search.ethiopian_from == False and search.ethiopian_to != False:
#                 _logger.info("################# From - f  To - true")

#                 today = datetime.now()
#                 today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
#                 return {'from': today, 'to': search.ethiopian_to}
#             elif search.ethiopian_from !=  False and search.ethiopian_to == False:
#                 _logger.info("################# From - true  To - false")
                            
#                 today = datetime.now()
#                 today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
#                 return {'from': search.ethiopian_from, 'to': today}
#             elif search.ethiopian_from ==  False and search.ethiopian_to ==  False:
#                 _logger.info("################# both- false")
                            
#                 today = datetime.now()
#                 today = EthiopianDateConverter.to_ethiopian(today.year,today.month,today.day)
#                 return {'from': today, 'to': today}
            
#             else:
#                 date = datetime.now()
#                 date = EthiopianDateConverter.to_ethiopian(date.year,date.month,date.day)
#                 _logger.info("################# d: %s",date)

#                 return date
    

#     @api.model
#     def date_convert_and_set(self,picked_date):
#         try:
#             dd = picked_date['url'].split('id=')
#             id = str(dd[1]).split('&')
#             m = picked_date['url'].split('model=')
#             mm = m[1].split('&')
#             if len(id[0]) <= 0:
#                 _logger.info("################# not fund")

#             else:
#                     _logger.info("lol")
#                     models = mm[0]
#                     search = self.env[models].search([('id','=',id[0])])
#                     date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
#                     date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
#                     # values = []
#                     # vals = {
#                     #     "date_from": '',
#                     #     "date_to": '',

#                     #     "pagum": '',
#                     #     "ethiopian_from": '',
#                     #     "ethiopian_to": '',

#                     # }
#                     # if int(picked_date['month']) == 13:
#                     #     _logger.info("YYYYYY")
#                     #     vals['date_from'] = date_gr
#                     #     vals['pagum'] = date
#                     #     values.append(vals)
#                     # else:
#                     #     _logger.info("FFFFFFFFFF")

#                     #     values['date_from'] = date_gr
#                     #     values['pagum'] = date
#                     #     values.append(vals)

#                     #     _logger.info("VVVVVVVVVVVVv Value:%s",values)


#                     if models == "reconciliation.time.fream":
#                         if picked_date['pick'] == 1:
#                             if int(picked_date['month']) == 13:
#                                 search.update({
#                                 'date_from': date_gr,
#                                 'pagum_from': date,
#                                 'is_pagum_from': False,
#                                 'ethiopian_from': None
#                                 })
#                                 search.action_reload_page()
#                             elif int(picked_date['month']) == 2 and int(picked_date['day']) > 28:
#                                 search.update({
#                                 'date_from': date_gr,
#                                 'pagum_from': date,
#                                 'is_pagum_from': False,
#                                 'ethiopian_from': None

#                                 })
#                                 search.action_reload_page()
#                             else:
#                                 search.update({
#                                 'date_from': date_gr,
#                                 'ethiopian_from': date,
#                                 'is_pagum_from': True,
#                                 'pagum_from': " "

#                                 })
#                                 search.action_reload_page()
                            
#                             # return {
#                             #         'type': 'ir.actions.client',
#                             #         'tag': 'reload',
#                             #     }
#                             # self.env.cr.commit()
#                             # return search
#                             search.action_reload_page()
                            

#                         if picked_date['pick'] == 2:
#                             if int(picked_date['month']) == 13:

#                                 search.write({
#                                     'date_to': date_gr,
#                                     'pagum_to':date, 
#                                     'is_pagum_to': False,
#                                     'ethiopian_to': None



#                                     })
#                             elif int(picked_date['month']) == 2 and int(picked_date['day']) > 28:
#                                 search.write({
#                                 'date_to': date_gr,
#                                 'pagum_to': date,
#                                 'is_pagum_to': False,
#                                 'ethiopian_to': None

#                                 })
#                                 search.action_reload_page()
#                             else:
#                                 search.write({
#                                     'date_to': date_gr,
#                                     'ethiopian_to':date,
#                                     'is_pagum_to': True,
#                                     'pagum_to': " "


#                                     })
#                             # return {
#                             #         'type': 'ir.actions.client',
#                             #         'tag': 'reload',
#                             #     }
#                             # self.env.cr.commit()
#                             # return search 
#                             search.action_reload_page()
                    
#                     return {
#                         'type': 'ir.actions.client',
#                         'tag': 'reload',
#                     }
                    
       

#         except:
#             pass
#         date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
#         date,time = str(datetime.now()).split(" ")
#         _logger.info(str(date_gr) + " " + str(f"{time}"))
#         dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
#         # date = str(date_et) + " " + str(f"{time}")
#         date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
#         date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
#         data = {
#             'day':   picked_date['day'],
#             'month': picked_date['month'],
#             'year': picked_date['year'],
#             'pick': picked_date['pick']
#         }
#         if picked_date['pick'] == 1:
#             pick1.append(data)
#         if picked_date['pick'] == 2:
#             pick2.append(data)
#         if picked_date['pick'] == 3:
#             pick3.append(data)
#         if picked_date['pick'] == 4:
#             pick3.append(data)







# class ResPartner(models.Model):
#     _inherit = 'res.partner'
    

#     # date = fields.Date(string=" Date")
#     ethiopian_date = fields.Date('Ethiopian Date |')
#     # ticked_user = fields.Many2one('res.users')

    


#     @api.model
#     def create(self, vals):
#         for i in range(0, len(pick1)):
  
#             if i == (len(pick1)-1):
#                 date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
#                 Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
#                 if pick1[i]['pick'] == 1:
#                     vals['date'] = date1
#                     vals['ethiopian_date'] = Edate1
#                     pick1.clear()
                
        
#         try:
#             if vals['date']  is not None:
#                 date1 = vals['date']
#                 Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
#                 vals['ethiopian_date'] = Edate1

#         except:
#             pass
       
#         return super(ResPartner, self).create(vals)




#     def write(self, vals):
#         _logger.info("############# Write:%s",vals)
#         try:
#             if vals['date'] is not None:
#                 date_str = vals['date']
#                 date_time_obj = date_str.split('-')
#                 Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
#                 vals['ethiopian_date'] = Edate
#         except:
#             pass
#         # self.action_reload_page()
#         return super(ResPartner, self).write(vals)




#     @api.model
#     def date_convert_and_set(self,picked_date):
#         try:
#             dd = picked_date['url'].split('id=')
#             id = str(dd[1]).split('&')
#             m = picked_date['url'].split('model=')
#             mm = m[1].split('&')
#             if len(id[0]) <= 0:
#                 _logger.info("################# not fund")

#             else: 
#                     models = mm[0]
#                     search = self.env[models].search([('id','=',id[0])])
#                     date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
#                     date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
#                     if models == "res.partner":
#                         if picked_date['pick'] == 1:
#                             search.update({
#                                 'date': date_gr,
#                                 'ethiopian_date': date
#                                 })
#                             # return {
#                             #         'type': 'ir.actions.client',
#                             #         'tag': 'reload',
#                             #     }
#                             # self.env.cr.commit()
#                             # return search
#                             search.action_reload_page()
                            
#                     return {
#                         'type': 'ir.actions.client',
#                         'tag': 'reload',
#                     }
       

#         except:
#             pass
#         date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
#         date,time = str(datetime.now()).split(" ")
#         _logger.info(str(date_gr) + " " + str(f"{time}"))
#         dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
#         # date = str(date_et) + " " + str(f"{time}")
#         date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
#         date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
#         data = {
#             'day':   picked_date['day'],
#             'month': picked_date['month'],
#             'year': picked_date['year'],
#             'pick': picked_date['pick']
#         }
#         if picked_date['pick'] == 1:
#             pick1.append(data)
#         if picked_date['pick'] == 2:
#             pick2.append(data)
#         if picked_date['pick'] == 3:
#             pick3.append(data)
#         if picked_date['pick'] == 4:
#             pick3.append(data)



 


