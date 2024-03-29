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
var EthiopianCalendarWidgetFour = Widget.extend({
  template: 'ethiopian_calander_widget_four',
  events:{},

start: function() {
  console.log("##### Ethiopian Calander Widget Four ####")
  var def = new $.Deferred();
  let picked_date = [];
  let clicked_val = [];
  this._super();
  // this.$input = this.$('input.o_datepicker_input');
  var self = this;
  console.log("This",this)
  var updateFormViewField1 = {
      dataPointID: this.getParent().__parentedParent.initialState.id,
      // changes: {'ethiopian_to': '2000-01-02'},
  };
  var callTrigger = this.trigger_up
  $(function() {
      var current_url = window.location.href;
      var myArray = current_url.split("&");
      var current_model = myArray[2].replace('model=',''); 
      var calendar = $.calendars.instance('ethiopian','am');
      var new_date = new Date();
      let pickeddate = {
          "current_model": current_model,
          "url": current_url,
          "pick": 4,
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
          var dateTo =  (data.four).length
                if(dateTo > 0){
                    //console.log("**** Both True")
                    var  date4 = data['four'].toString()
                    date4 = data['four'].split("-")

                    if (date4[1] === undefined){
                      var date44 = data['four'].split("/")
                      var dateFour = date44[0] + "/" +  date44[1] + "/" +  date44[2]
                      var dateFour = date44[0] + "/" + date44[1] + "/" +  date44[2]
                      localStorage.setItem('myFlag4', dateFour);
                       $("#DatepickerFour").val(dateFour);
                   }else{

                    var dateFour = date4[1] + "/" +  date4[2] + "/" +  date4[0]
                    //console.log(" From GGGGGG date:",date1)
                    // $("#DatepickerThree").val(dateFrom);
                    localStorage.setItem('myFlag4', data['four']);
                    $("#DatepickerFour").val(dateFour);
                   }
                }else{
                        //console.log("--- Both False")
                        var  date = data.toString()
                        date = date.split("-")
                        var dates = date[1] + "/" +  date[2] + "/" +  date[0]
                        initial_date.push(dates)
                        var myFlag4 = localStorage.getItem('myFlag4');
                        console.log("intial 1", myFlag4)
                      //  $("#DatepickerThree").val(dates);
                       $("#DatepickerFour").val(dates);
                        localStorage.setItem('myFlag4', date);
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
   
      $('#DatepickerFour').calendarsPicker({calendar: calendar,onSelect:function()
      {
        var dateObject = $(this).calendarsPicker("getDate")
          let pickeddate = {
                  "day" : dateObject[0]._day,
                  "month" : dateObject[0]._month,
                  "year":dateObject[0]._year,
                  "current_model": current_model,
                  "url": current_url,
                  "pick": 4,

                  }
                  var dd,model;
                  console.log("Picked:",pickeddate)
                  dd = current_url.split('model=')
                  model = dd[1].toString()
                  model = model.split('&')
                  console.log("############ id",model)
                  console.log("############ Model",model[0])
                  var res = rpc.query({
                            model: model[0],
                            method: 'date_convert_and_set',
                            args: [pickeddate],
                        }).then(function (data)
                        {
                        console.log("Response of payment",data)
                        // console.log("Refresh...1111111111111111")
        
                        // $("#popupDatepicker" ).datepicker("refresh");
                    });
                  let val = 0
                }});
            });
             
  var Inputvalue4 = $('#DatepickerFour').val();
  if(Inputvalue4 != null){
  if(parseInt(Inputvalue4.length) > 1){
  var Inputvalue4 = $('#DatepickerFour').val();
      Inputvalue4 = Inputvalue4.split("/")
      var value =  Inputvalue4[2]+'-'+Inputvalue4[0]+'-'+Inputvalue4[1]
      var updateFormViewField = {
          dataPointID: updateFormViewField1.dataPointID,
          changes: {'ethiopian_four': value},
        }
      var myFlag4 = localStorage.getItem('myFlag4');
        console.log('flag..', myFlag4,value);
        if (myFlag4 != value){
               console.log('has differncr',myFlag4,value);
               localStorage.setItem('myFlag4', value);
               var myFlag4 = localStorage.getItem('myFlag4');
               console.log('updateFormViewField',value);
               return this.trigger_up('field_changed', updateFormViewField);
              }
  }
  else{
      //console.log("FFFFFFFFFFFFFFFFFFFF")
      // $("#popupDatepicker").val('01/01/2020');
      // $("#DatepickerFour").val('01/01/2020');
  }
  }   
},
});

widget_registry.add('ethiopian_calander_widget_four', EthiopianCalendarWidgetFour)
});



