
import random
import string
import werkzeug.urls

from collections import defaultdict
from datetime import datetime, timedelta, date
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
import logging
_logger = logging.getLogger(__name__)
import calendar

class CalanderEventInherit(models.Model):
    _inherit = 'calendar.event'

    is_gerated_date = fields.Boolean(default=False)
    is_ethiopian_calander = fields.Boolean(default=False)
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
        # Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
        # month = monthNames[int(Edate1.month)+1].split(' ')[0]
        # ethioDay = Ethio_numbers[int(Edate1.day)].split(' ')[0]
        # # month  = month.split(',')
        # # _logger.info("tttttttttttttttt %s",month[0])
        # value = str(month) +"-"+ str(Edate1.day) +"-"+ str(Edate1.year) +"----------------------"+ ethioDay
        # now = datetime.now()
        # startStamp = now.strftime('%Y-%m-%d %H:%M:%S')
        # get_value = self.env['calendar.event'].search([('is_gerated_date','=',True)])
        # for line in get_value:
        #     delete = line.unlinkAutoGenerateValues()
        partners = self.env['res.users'].search([('share','=',False)])
        partner_ids = []

        for users in partners:
            if users.partner_id is not None:
                partner_ids.append(users.partner_id.id)
            else:
                pass

        year = 2021
        month = 2 # February

        num_days = calendar.monthrange(date1.year, date1.month)[1]
        f_date = date(date1.year,date1.month, 1)
       
        for da in range(int(num_days)):
                a_date1 = (f_date + timedelta(days = da)).isoformat()
                a_date = str(a_date1).split('-')
                Edate1 = EthiopianDateConverter.to_ethiopian(int(a_date[0]),int(a_date[1]),int(a_date[2]))
                if type(Edate1) ==   date:
                    month = monthNames[int(Edate1.month)].split(' ')[0]
                    ethioDay = Ethio_numbers[int(Edate1.day)].split(' ')[0]
                    value = str(month) +"-" +str(Edate1.day) +"("+ str(ethioDay) +")" +"-"+ str(Edate1.year)
                    create = self.env['calendar.event'].create({
                        'name': value,
                        'create_uid': self.env.user.id,
                        'create_date': datetime.now(),
                        'write_uid': self.env.user.id,
                        'write_date':datetime.now(),
                        'allday': True,
                        'start': a_date1,
                        'stop': a_date1,
                        'is_gerated_date': True,
                        'partner_ids': partner_ids
                    })
                if type(Edate1) ==   str:
                    Edate1 = Edate1.split('/')
                    month = monthNames[int(Edate1[0])].split(' ')[0]
                    ethioDay = Ethio_numbers[int(Edate1[1])].split(' ')[0]
                    # month  = month.split(',')
                    # _logger.info("tttttttttttttttt %s",month[0])
                    value = str(month) +"-"+ str(ethioDay) +str(Edate1[1])+ "("+str(ethioDay)+")"+"-"+ str(Edate1[2])
                    _logger.info("tttttttvaluevaluettttttttt %s",value)
                    create = self.env['calendar.event'].create({
                        'name': value,
                        'create_uid': self.env.user.id,
                        'create_date': datetime.now(),
                        'write_uid': self.env.user.id,
                        'write_date':datetime.now(),
                        'allday': True,
                        'start': a_date1,
                        'stop': a_date1,
                        'is_gerated_date': True,
                        'partner_ids': partner_ids
                    })
        # create['partner_id'] = [(6,0, (11,79))]
        return True
    

    def unlink(self):
        search = self.env['calendar.event'].search([('id','=',self.id)])
        try:
            if search.is_gerated_date == True:
                pass
            else:
                return super(CalanderEventInherit, self).unlink()
        except:
            pass

    def write(self, vals):
        search = self.env['calendar.event'].search([('id','=',self.id)])
        try:
            if search.is_gerated_date == True:
                pass
            else:
                return super(CalanderEventInherit, self).write(vals)
        except:
            pass
        


 
