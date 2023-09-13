
odoo.define(function(require){
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
    var rpc = require('web.rpc')
    var EthiopianCalendarWidget = Widget.extend({
                template: 'ethiopian_calander_widget',
                
                events:{},
            
            start: function() {
                //console.log("##### Ethiopian Calander Widget one####")
                var def = new $.Deferred();
                let picked_date = [];
                let clicked_val = [];
                this._super();
                // this.$input = this.$('input.o_datepicker_input');
                // //console.log("##########",this.$input)
                var self = this;
                //console.log("This",this)
                var updateFormViewField1 = {
                    dataPointID: this.getParent().__parentedParent.initialState.id,
                    changes: {'ethiopian_from': '2000-01-02'},
                };
                var callTrigger = this.trigger_up
                $(function() {
                    var current_url = window.location.href;
                    //console.log("current_url",current_url)
                    var myArray = current_url.split("&");
                    var current_model = myArray[2].replace('model=',''); 
                    //console.log("current model",current_model)
                    //console.log("myArray[2]",myArray[2])
                    //console.log('session',session)
                    var calendar = $.calendars.instance('ethiopian','am');
                    var new_date = new Date();
                    //console.log(new_date)
                    let pickeddate = {
                        "current_model": current_model,
                        "url": current_url,
                        "pick": 1,
                    }
                     try{
                         var dd,model;
                         dd = current_url.split('model=')
                         model = dd[1].toString()
                         model = model.split('&')
                         var res = rpc.query({
                             model: model[0],
                             method: 'initial_date',
                             args: [pickeddate],
                         }).then(function(data)
                         {
                         //console.log("Response", data)
                         try{
                                 var dateFrom =  (data.from).length
                                 console.log("dddddddddddd", data.from)
                                 if(dateFrom > 0){
                                     console.log("**** Both True")
                                     var  date1 = data['from'].toString()
                                     date1 = data['from'].split("-")
                                     var dateFrom = date1[1] + "/" +  date1[2] + "/" +  date1[0]
                                     //console.log(" From GGGGGG date:",date1)
                                     $("#popupDatepicker").val(dateFrom);
                                     localStorage.setItem('myFlag', data['from']);
                                 }else{
                                         //console.log("--- Both False")
                                         var  date = data.toString()
                                         date = date.split("-")
                                         var dates = date[1] + "/" +  date[2] + "/" +  date[0]
                                         initial_date.push(dates)
                                         var myFlag = localStorage.getItem('myFlag');
                                         console.log("intial 1", myFlag)
                                        $("#popupDatepicker").val(dates);
                                        // $("#DatepickerTwo").val(dates);
                                         localStorage.setItem('myFlag', date);
                                         }
                    
                             }
                             catch (error) {
                                 // code that handles the error
                                 //console.log('There was an error:', error);
                         }
                             });
                   
                     }catch (error) {
                             // code that handles the error
                             //console.log('There was an error:', error);
                         }
                 
                    $('#popupDatepicker').calendarsPicker({calendar: calendar,onSelect:function()
                    {
                      var dateObject = $(this).calendarsPicker("getDate")
                      //console.log("dateObject", dateObject)
                        let pickeddate = {
                                "day" : dateObject[0]._day,
                                "month" : dateObject[0]._month,
                                "year":dateObject[0]._year,
                                "current_model": current_model,
                                "url": current_url,
                                "pick": 1,
                                }
                      var dd,model;
                      //console.log("Picked:",pickeddate)
                      let val = 0
                      dd = current_url.split('model=')
                      model = dd[1].toString()
                      model = model.split('&')
                      var res = rpc.query({
                                model: model[0],
                                method: 'date_convert_and_set',
                                args: [pickeddate],
                            }).then(function (data)
                            {
                        }); 
                    }}); 
                });
                    var Inputvalue = $('#popupDatepicker').val();
                    if(Inputvalue != null){
                    if(parseInt(Inputvalue.length) > 1){
                    var Inputvalue = $('#popupDatepicker').val();
                        Inputvalue = Inputvalue.split("/")
                        var value =  Inputvalue[2]+'-'+Inputvalue[0]+'-'+Inputvalue[1]
                        var updateFormViewField = {
                            dataPointID: updateFormViewField1.dataPointID,
                            changes: {'ethiopian_from': value},
                          }
                        var myFlag = localStorage.getItem('myFlag');
                          console.log('flag..', myFlag,value);
                          if (myFlag != value){
                                 console.log('has differncr',myFlag,value);
                                 localStorage.setItem('myFlag', value);
                                 var myFlag = localStorage.getItem('myFlag');
                                 console.log('updateFormViewField',value);
                                 return this.trigger_up('field_changed', updateFormViewField);
                                }
                    }
                    else{
                        //console.log("FFFFFFFFFFFFFFFFFFFF")
                        // $("#popupDatepicker").val('01/01/2020');
                        // $("#DatepickerTwo").val('01/01/2020');
                    }
                }
            },
        });

        widget_registry.add('ethiopian_calander_widget', EthiopianCalendarWidget)


});


