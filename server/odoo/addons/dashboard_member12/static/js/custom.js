$(function() {
  var calendar = $.calendars.instance('ethiopian','am');
 $('#Date').calendarsPicker({calendar: calendar});
});
// console.log("********** supporter*********11")

// odoo.define('dashboard_member12.supporter', function (require) {
//     'use strict';
// console.log("********** supporter*********22")


//     var publicWidget = require('web.public.widget');
//     const {_t, qweb} = require('web.core');

//     publicWidget.registry.SupportersPhoneValidation = publicWidget.Widget.extend({

//         selector: '.o_phone_number_validation',
//         // read_events: {
//         //     'change select[name="supporter_phone_member"]': '_transferChange',
//         // },

//         start: function () {

//             // var $phone = this.$('select[name="supporter_phone_member"]');
//             // console.log("^^^^^^^^^^^^^^^^^^^^^^^^^^^^",$phone)

//             var def = this._super.apply(this, arguments);
//             return def;

            
//         },

        

//         // _tempChange: function() {
//         //     var $phone = this.$('select[name="supporter_phone_member"]');
//         //     console.log("^^^^^^^^^^^^^^^^^^^^^^^^^^^^",$phone)
       
//         // },
//         // _transferChange: function() {
//         //     this._tempChange()
//         // },
//     });


// });