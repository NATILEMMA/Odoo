console.log("##### Ethiopian Calander Widget one####")
odoo.define("EthiopianCalendar.EthiopianCalendarWidget", function(require){
    "use strict";
    var core = require('web.core');
    var time = require('web.time');
    var field_utils = require('web.field_utils');
    var session = require('web.session');
    var _t = core._t;
    var qweb = core.qweb;
    var config = require('web.config');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');
    var view_dialogs = require('web.view_dialogs');
    var widget_registry = require("web.widget_registry");
    // var rpc = require('web.rpc')
    // let clicked_val = 0
    var session = require('web.session');
    var rpc = require('web.rpc')
    let clicked_val = 0
   
    
    var EthiopianCalendarWidget = Widget.extend({
                template: 'ethiopian_calander_widget',
                
                events:{},
            
            start: function() {
                var def = new $.Deferred();
                let picked_date = [];
                let initial_date = []
                var current_url = window.location.href;
                // console.log("current_url",current_url)
                // var myArray = current_url.split("&");
                // var current_model = myArray[2].replace('model=',''); 
                // // console.log("current model",current_model)
                // // console.log("myArray[2]",myArray[2])
                // // console.log('session',session)

                // this._super();
                // // this.$input = this.$('input.o_datepicker_input');
                // console.log("######ffffffffgggffffffff####",this)
                // var self = this;

                // let pickeddate = {
                //     "current_model": current_model,
                //     "url": current_url,
                //     "pick": 1,
                // }
               
                // try{
                //     var dd,model;
                //     dd = current_url.split('model=')
                //     model = dd[1].toString()
                //     model = model.split('&')
                //     var res = rpc.query({
                //         model: model[0],
                //         method: 'initial_date',
                //         args: [pickeddate],
                //     }).then(function(data)
                //     {
                //     console.log("Response", data)
                //     try{
                //             var dateFrom =  (data.from).length 
                //             var dateTo =  (data.to).length 
                //             console.log(dateFrom, dateTo)
                //             if(dateFrom > 0 && dateTo > 0){
                //                 console.log("**** Both True")
                //                 var  date1 = data['from'].toString()
                //                 date1 = data['from'].split("-")
                //                 var  date2 = data['to'].toString()
                //                 date2 = data['to'].split("-")
                            

                //                 var dateFrom = date1[1] + "/" +  date1[2] + "/" +  date1[0]
                //                 var dateTo = date2[1] + "/" +  date2[2] + "/" +  date2[0]


                //                 console.log(" From GGGGGG date:",date1)
                //                 $("#popupDatepicker").val(dateFrom);
                //                 $("#DatepickerTwo").val( dateTo);


                //             }else{
                //                     console.log("--- Both False")
                //                     var  date = data.toString()
                //                     date = date.split("-")
                //                     console.log("Response", date[0])
                //                     console.log("Response", date[1])
                //                     console.log("Response", date[2])
                //                     var dates = date[1] + "/" +  date[2] + "/" +  date[0]
                //                     console.log("GGGGGG Today GGGGGGG date:",dates)
                //                     initial_date.push(dates)

                //                     $("#popupDatepicker").val(dates);
                //                     $("#DatepickerTwo").val(dates);
                //                     }
                
                //         }
                //         catch (error) {
                //             // code that handles the error
                //             console.log('There was an error:', error);
                //     }
                //         });
               
                // }catch (error) {
                //         // code that handles the error
                //         console.log('There was an error:', error);
                //     }
            //     try{
            //         var Inputvalue = $('#popupDatepicker').val();
            //         console.log("PPPPPPPPPPPPPPffPPPPP ",Inputvalue)
            //         var  Inputvalue = Inputvalue.toString()
            //         Inputvalue = Inputvalue.split("/")

            //         let pickeddates = {
            //             "day" : Inputvalue[1],
            //             "month" : Inputvalue[0],
            //             "year":Inputvalue[2],
            //             "current_model": current_model,
            //             "url": current_url,
            //             "pick": 1,

            //             }

            //         console.log("KKKpickeddates ",pickeddates)

            //     //     var res = rpc.query({
            //     //         model: model[0],
            //     //         method: 'date_convert_and_set',
            //     //         args: [pickeddates],
            //     //     }).then(function (data)
            //     //     {
            //     //     console.log("MMMMMMMMMMM of payment",data)
            //     // });
            // }catch (error) {
            //     // code that handles the error
            //     console.log('There was an error:', error);
            //   }


                // console.log("IIIIId",initial_date)
                // console.log("II",initial_date[0])

                // // $("#popupDatepicker").datepicker( "setDate" , "04/18/2023");
                $(function() {
                // $("#popupDatepicker").datepicker("setDate", '04/05/2015');
                // $("#DatepickerTwo").datepicker( "setDate" , '04/05/2015');

                    var calendar = $.calendars.instance('ethiopian','am');
                    $('#popupDatepicker').calendarsPicker({calendar: calendar,onSelect: showDate});
                    // var pickeddate = showDate
                    // picked_date = showDate(date)
                    // console.log("pickedate",picked_date)
                });

                async function showDate(date) {
                                    console.log("Mainfeedback",date)
                                    let pickeddate = {
                                    "day" : date[0]._day,
                                    "month" : date[0]._month,
                                    "year":date[0]._year
                                    }
                    
                    //                   
                    
                                }

    
                // console.log("reffffffffffffffffffff---------------")
                // $("#popupDatepicker" ).datepicker("refresh");
                // $("#DatepickerTwo" ).datepicker("refresh");

            },
         
        
            
        });

        widget_registry.add('ethiopian_calander_widget', EthiopianCalendarWidget)


//         var EthiopianCalendarWidget = Widget.extend({
//             template: 'ethiopian_calander_widget',
            
//             events:{},
        
//         start: function() {
//             var def = new $.Deferred();
//             let picked_date = [];
//             this._super();
//             // this.$input = this.$('input.o_datepicker_input');
//             console.log("##########",this)
//             var self = this;
//             $(function() {
//                 var calendar = $.calendars.instance('ethiopian','am');
//                 $('#popupDatepicker').calendarsPicker({calendar: calendar,onSelect: showDate});
//                 // var pickeddate = showDate
//                 // picked_date = showDate(date)
//                 // console.log("pickedate",picked_date)
//             });

//             async function showDate(date) {
//                 console.log("Mainfeedback",date)
//                 let pickeddate = {
//                 "day" : date[0]._day,
//                 "month" : date[0]._month,
//                 "year":date[0]._year
//                 }

// //                   

//             }
//         },
     
    
        
//     });

//     widget_registry.add('ethiopian_calander_widget_three', EthiopianCalendarWidget)



        

});



