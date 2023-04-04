odoo.define('CustomCalendar.ETHIOPIANCalendar', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var web_client = require('web.web_client');
    var session = require('web.session');
    var _t = core._t;
    var QWeb = core.qweb;
    var self = this;
    var currency;
    var DashBoard = AbstractAction.extend({
        contentTemplate: 'ETHIOPIANCalendar',
     
        init: function(parent, context) {
            this._super(parent, context);
            this.upcoming_events = [];
            this.dashboards_templates = ['LoginUser','Managercrm','Admincrm', 'SubDashboard'];
            this.login_employee = [];

            console.log("################")
            location.reload()
        },

        start: function() {
            var def = new $.Deferred();
            let picked_date = [];
            this._super();
            // this.$input = this.$('input.o_datepicker_input');
            // console.log("##########",this.$input)
            var self = this;
            $(function() {
                console.log("clicked......")
                var calendar = $.calendars.instance('ethiopian','am');
                $('#popupDatepicker').calendarsPicker({calendar: calendar,onSelect: showDate});
                // var pickeddate = showDate
                // picked_date = showDate(date)
                console.log("calendar",calendar)
            });

            async function showDate(date) {
                console.log("Mainfeedback",date)
                let pickeddate = {
                "day" : date[0]._day,
                "month" : date[0]._month,
                "year":date[0]._year
                }

                picked_date.push(pickeddate)
                console.log(picked_date)
                let Postdate = await self._rpc({
                            model: 'res.partner',
                            // rout: `/get_order`,
                            method: 'date_convert_and_set',
                            args: [picked_date],
                        })
        

            } 
            
            console.log("VALue:",picked_date)    
        },

        

       
    });

    core.action_registry.add('CustomCalendar', DashBoard);
    return DashBoard;
});