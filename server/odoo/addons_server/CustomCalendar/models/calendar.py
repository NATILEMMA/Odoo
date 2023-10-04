
import random
import string
import werkzeug.urls
import requests
import json
from collections import defaultdict
from datetime import datetime, timedelta, date
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
import logging
_logger = logging.getLogger(__name__)
import calendar
import pprint

class Holiday(models.Model):
    _name = 'holiday.interval'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    year_from = fields.Char("From", translate=True)
    year_to = fields.Char("TO", translate=True)

class Year(models.Model):
    _name = 'year.interval'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    year_from = fields.Char("From", translate=True)
    year_to = fields.Char("To", translate=True)

class Month(models.Model):
    _name = 'month.interval'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    month_from = fields.Char("From", translate=True)
    month_to = fields.Char("To", translate=True)

class ResUsers(models.Model):
    _inherit = 'res.users'

    
    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        if vals.get('sel_groups_1_8_9') == 1:
            self.env.cr.execute("INSERT INTO calendar_event_res_partner_rel(res_partner_id ,calendar_event_id ) select %s,id from calendar_event where is_generated_date = True"%(res.partner_id.id))
            self.env.cr.commit()
            get_default_role = self.env['res.users.role'].sudo().search([('is_general','=',True)])
            roles= []
            for role in get_default_role:
                if role.name == 'Ethiopian datepicker role':
                    roles.append((0, 0, {
                                'role_id': role.id,
                                'is_enabled': False
                                }))
                else:
                    roles.append((0, 0, {
                                'role_id': role.id,
                                'is_enabled': True
                                }))
            res.role_line_ids = roles
            # self.env.cr.commit()
        return res
    

       
    def generat_general_group(self):
        try:
            gro_groups = self.env['res.groups'].search([('name','=','Gregory Datepicker')], limit=1)
            ethio_groups = self.env['res.groups'].search([('name','=','Ethiopian Datepicker')], limit=1)
            res_users = self.env['res.users'].search([('share', '=', False)])
            
            ethio_user_list = []
            gro_user_list = []
            if ethio_groups.users is not None:
                    if self.env.user in ethio_groups.users: 
                        pass
            for user in res_users:
                if user in ethio_groups.users:
                    pass
                else:
                    gro_user_list.append(user.id)
                gro_groups['users'] = [(6,0,gro_user_list)]
        except:
            pass

class CalanderEventInherit(models.Model):
    _inherit = 'calendar.event'

    is_holiday = fields.Boolean(default=False)
    # is_ethiopian_calander = fields.Boolean(default=False)
    @api.onchange('your_toggle_field')
    def on_toggle_button(self):
        if self.your_toggle_field:
            pass
            # do something when toggle button is turned on
        else:
            pass
            # do something when toggle button is turned off
    def unlinkAutoGenerateValues(self):
        return super(CalanderEventInherit, self).unlink()
    


    def auto_generate(self):  
        monthNames =  ['0','መስከረም', 'ጥቅምት', 'ኅዳር','ታህሣሥ', 'ጥር', 'የካቲት',
		                'መጋቢት','ሚያዝያ','ግንቦት','ሰኔ','ሐምሌ', 'ነሐሴ','ጳጉሜ']
        Ethio_numbers = ['0','፩','፪','፫','፬','፭','፮','፯','፰','፱','፲',
                        '፲፩','፲፪','፲፫','፲፬','፲፭','፲፮','፲፯','፲፰','፲፱','፳',
                        '፳፩','፳፪','፳፫','፳፬','፳፭','፳፮','፳፯','፳፰','፳፱','፴']
        
        MonthNamess =  [('መስከረም','1'), ('ጥቅምት','2'), ('ኅዳር','3'), ('ታህሣሥ','4'), ('ጥር','5'), ('የካቲት','6'),
		            ('መጋቢት','7'), ('ሚያዝያ','8'), ('ግንቦት','9'), ('ሰኔ','10'), ('ሐምሌ','11'), ('ነሐሴ','12'), ('ጳጉሜ','12')]
        numbers = [('፩','1'),('፪','2'),('፫','3'),('፬','4'),('፭','5'),('፮','6'),('፯','7'),('፰','8'),('፱','8'),('፩','9'),('፲','10'),
                   ('፲፩','11'),('፲፪','12'),('፲፫','13'),('፲፬','14'),('፲፭','15'),('፲፮','16'),('፲፯','17'),('፲፰','18'),('፲፱','19'),('፩','20'),
                   ('፩፩','21'),('፩፪','22'),('፩፫','23'),('፩፬','24'),('፩፭','25'),('፩፮','26'),('፩፯','27'),('፩፰','28'),('፩፱','29'),('፴','30'),]
        months = [('1', 'January'),('2', 'February'),('3', 'March'),('4', 'April'),('5', 'May'),('6', 'June'),('7', 'July'),('8', 'August'), ('9', 'September'),('10', 'October'), ('11', 'November'), ('12', 'December')]
        # month_name = dict(months).get(vals.get('month'))
        date1 = datetime.now()
        startDate = date(date1.year-5,1, 1)
        endDate = date(date1.year+5, 1, 1)
        _logger.info(startDate)
        _logger.info(endDate)

        for year in range(startDate.year, endDate.year):
            for month in range(1, 13):
                search = self.env['res.users'].search([('name','=','Ethiopian Calendar')])
                if len(search) > 0:
                    pass
                else:
                    user = self.env['res.users'].create({
                        'name': 'Ethiopian Calendar',
                        'login': 'ET',
                        'email': 'ET@example.com',
                        'password': 'password',
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
                    })
                search = self.env['res.users'].search([('name','=','Holidays')])
                if len(search) > 0:
                    pass
                else:
                    user = self.env['res.users'].create({
                        'name': 'Holidays',
                        'login': 'HD',
                        'email': 'DH@example.com',
                        'password': 'password',
                        'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
                    })
                partners = self.env['res.users'].search([('id','=',2)])
                partner_ids = []
                for users in partners:
                    if users.partner_id is not None:
                        partner_ids.append(users.partner_id.id)
                    else:
                        pass

                

                
                # year = 2021
                # month = 4 # February
                num_days = calendar.monthrange(year, month)[1]
                f_date = date(year,month, 1)
                et = self.env['res.users'].search([('name','=','Ethiopian Calendar')], limit=1)
                hd = self.env['res.users'].search([('name','=','Holidays')], limit=1)
            
                for da in range(int(num_days)):
                        a_date1 = (f_date + timedelta(days = da)).isoformat()
                        a_date = str(a_date1).split('-')
                        Edate1 = EthiopianDateConverter.to_ethiopian(int(a_date[0]),int(a_date[1]),int(a_date[2]))
                        if type(Edate1) ==   date:
                            month = monthNames[int(Edate1.month)].split(' ')[0]
                            ethioDay = Ethio_numbers[int(Edate1.day)].split(' ')[0]
                            value = str(month) +"-" +str(Edate1.day) +"("+ str(ethioDay) +")" +"-"+ str(Edate1.year)
                        
                            search = self.env['calendar.event'].search([('start','=',a_date1),('name','=', value)])
                            if len(search) > 0:
                                search.update({'partner_ids': partner_ids})
                                search['partner_ids'] = [(6,0, (partner_ids))]
                            else:
                                create = self.env['calendar.event'].create({
                                'name': value,
                                'user_id': et.id,
                                'create_uid': et.id,
                                'create_date': datetime.now(),
                                'write_uid': et.id,
                                'write_date':datetime.now(),
                                'allday': True,
                                'start': a_date1,
                                'stop': a_date1,
                                'is_generated_date': True,
                                'is_holiday': False,
                                'partner_ids': partner_ids
                                })
                        if type(Edate1) ==   str:
                            Edate1 = Edate1.split('/')
                            month = monthNames[int(Edate1[0])].split(' ')[0]
                            ethioDay = Ethio_numbers[int(Edate1[1])].split(' ')[0]
                            value = str(month) +"-"+ str(ethioDay) +str(Edate1[1])+ "("+str(ethioDay)+")"+"-"+ str(Edate1[2])
                            search = self.env['calendar.event'].search([('start','=',a_date1),('name','=', value)])
                            if len(search) > 0:
                                search.update({
                                        'partner_ids': partner_ids
                                    })
                            else:
                                create = self.env['calendar.event'].create({
                                'name': value,
                                'user_id': et.id,
                                'create_uid': et.id,
                                'create_date': datetime.now(),
                                'write_uid': et.id,
                                'write_date':datetime.now(),
                                'allday': True,
                                'start': a_date1,
                                'stop': a_date1,
                                'is_generated_date': True,
                                'is_holiday': False,
                                'partner_ids': partner_ids
                            })
        # create['partner_id'] = [(6,0, (11,79))]
        # self.AutoGenerateHolidayValues()

        return True
    
    def AutoGenerateHolidayValues(self):

       
        date1 = datetime.now()
        startDate = date(date1.year-5,1, 1)
        endDate = date(date1.year+5, 1, 1)
        partners = self.env['res.users'].search([('id','=',2)])
        partner_ids = []
        hd = self.env['res.users'].search([('name','=','Holidays')], limit=1)
        for users in partners:
            if users.partner_id is not None:
                partner_ids.append(users.partner_id.id)
            else:
                pass
        for year in range(startDate.year, endDate.year):
            url = "https://calendarific.com/api/v2/holidays?api_key=cf5724f67854d92263a14a3f69e04b670262c5bc&country=ET&year="+str(year)
            _logger.info("Url :%s",url)
        
            payload = json.dumps({})
            headers = {
                    'Content-Type': 'application/json',
                    'Cookie': 'PHPSESSID=v3tdp5b0d8dn5kud10gdrgm1gs'
                    }
            response = requests.request("GET", url, headers=headers, data=payload)
            _logger.info(pprint.pformat(response.json()))
            res = response.json()
            holiday = res['response']['holidays']

            for hol in holiday:
     
                Htype = str(hol['type']).split(" [' ")
                Htype = Htype[0].split("'")
                s_date = date(hol['date']['datetime']['year'],hol['date']['datetime']['month'], hol['date']['datetime']['day'])
                search = self.env['calendar.event'].search([('start','=',s_date),('name','=', hol['name'])])
                if len(search) > 0:
                    _logger.info("----------")
                else:
                    if Htype[1] == "National holiday":
                        create = self.env['calendar.event'].create({
                                'name': hol['name'],
                                'user_id': hd.id,
                                'create_uid': hd.id,
                                'create_date': datetime.now(),
                                'write_uid': hd.id,
                                'write_date':datetime.now(),
                                'allday': True,
                                'start': s_date,
                                'stop': s_date,
                                'is_generated_date': True,
                                'is_holiday': True,
                                'partner_ids': partner_ids
                        })
                        _logger.info("create:%s",create)
        # _logger.info("Date:%s",res['response']['holidays'][0]['date']['iso'])

        # groups = self.env['res.groups'].search([('name','=','Calendar group')], limit=1)
        # events = self.env['calendar.event'].search([('is_holiday', '=', True)])
        # groups['users'] = [(6,0,events)]
   

    def unlink(self):
        search = self.env['calendar.event'].search([('id','=',self.id)])
        try:
            if search.is_generated_date == True and search.is_holiday == False:
                pass
            else:
                return super(CalanderEventInherit, self).unlink()
        except:
            pass

    # def write(self, vals):
    #     search = self.env['calendar.event'].search([('id','=',self.id)])
    #     try:
    #         if search.is_generated_date == True and search.is_holiday == False:
    #             pass
    #         else:
    #             return super(CalanderEventInherit, self).write(vals)
    #     except:
    #         pass
        


 
