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
                  var dateFrom =  (data.from).length
                  var dateTo =  (data.to).length
                  //console.log(dateFrom, dateTo)
                  if(dateFrom > 0 && dateTo > 0){
                      //console.log("**** Both True")
                      var  date1 = data['from'].toString()
                      date1 = data['from'].split("-")
                      var  date2 = data['to'].toString()
                      date2 = data['to'].split("-")
                      var dateFrom = date1[1] + "/" +  date1[2] + "/" +  date1[0]
                      var dateTo = date2[1] + "/" +  date2[2] + "/" +  date2[0]
                      //console.log(" From GGGGGG date:",date1)
                      // $("#DatepickerThree").val(dateFrom);
                      localStorage.setItem('myFlag4', data['to']);
//                     localStorage.setItem('myFlag4', dateTo);
                      $("#DatepickerFour").val(dateTo);
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
            changes: {'ethiopian_fourth': value},
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



