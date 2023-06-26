console.log("##### Ethiopian Calander Widget Two####")
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
var EthiopianCalendarWidgetTwo = Widget.extend({
    template: 'ethiopian_calander_widget_two',
    
    events:{},
  
  start: function() {
    console.log("##### Ethiopian Calander Widget Two####")
  
    var def = new $.Deferred();
    let picked_date = [];
    let clicked_val = [];
    this._super();
    // this.$input = this.$('input.o_datepicker_input');
    var self = this;
    console.log("This",this)
    var updateFormViewField1 = {
        dataPointID: this.getParent().__parentedParent.initialState.id,
        // changes: {'ethiopian_from': '2000-01-02'},
    };
    var callTrigger = this.trigger_up
    $(function() {
    console.log("This1--",this)
        var current_url = window.location.href;
        console.log("current_url",current_url)
        var myArray = current_url.split("&");
        var current_model = myArray[2].replace('model=',''); 
        console.log("current model",current_model)
        console.log("myArray[2]",myArray[2])
        console.log('session',session)
        var calendar = $.calendars.instance('ethiopian','am');
        var new_date = new Date();
        console.log(new_date)
        let pickeddate = {
            "current_model": current_model,
            "url": current_url,
            "pick": 2,
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
                  console.log("dddddddddddd", data.from, data.to)

                  if(dateFrom > 0 && dateTo > 0){
                      //console.log("**** Both True")
                      var  date1 = data['from'].toString()
                      date1 = data['from'].split("-")
                      var  date2 = data['to'].toString()
                      date2 = data['to'].split("-")
                      var dateFrom = date1[1] + "/" +  date1[2] + "/" +  date1[0]
                      var dateTo = date2[1] + "/" +  date2[2] + "/" +  date2[0]
                      //console.log(" From GGGGGG date:",date1)
                      $("#popupDatepicker").val(dateFrom);
                      localStorage.setItem('myFlag1', data['to']);
//                                     localStorage.setItem('myFlag', dateTo);
                      $("#DatepickerTwo").val(dateTo);
                  }else{
                          //console.log("--- Both False")
                          var  date = data.toString()
                          date = date.split("-")
                          var dates = date[1] + "/" +  date[2] + "/" +  date[0]
                          initial_date.push(dates)
                          var myFlag1 = localStorage.getItem('myFlag1');
                          console.log("intial 1", myFlag1)
                         $("#popupDatepicker").val(dates);
                         $("#DatepickerTwo").val(dates);
                          localStorage.setItem('myFlag1', date);
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
  
     
        $('#DatepickerTwo').calendarsPicker({calendar: calendar,onSelect:function()
        {
          var dateObject = $(this).calendarsPicker("getDate")
          console.log("dateObject", dateObject)
            let pickeddate = {
                    "day" : dateObject[0]._day,
                    "month" : dateObject[0]._month,
                    "year":dateObject[0]._year,
                    "current_model": current_model,
                    "url": current_url,
                    "pick": 2,
  
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
     
  
    var Inputvalue1 = $('#DatepickerTwo').val();
    if(Inputvalue1 != null){
    if(parseInt(Inputvalue1.length) > 1){
    var Inputvalue1 = $('#DatepickerTwo').val();
        Inputvalue1 = Inputvalue1.split("/")
        var value =  Inputvalue1[2]+'-'+Inputvalue1[0]+'-'+Inputvalue1[1]
        var updateFormViewField = {
            dataPointID: updateFormViewField1.dataPointID,
            changes: {'ethiopian_to': value},
          }
        var myFlag1 = localStorage.getItem('myFlag1');
          console.log('flag..', myFlag1,value);
          if (myFlag1 != value){
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
  
  widget_registry.add('ethiopian_calander_widget_two', EthiopianCalendarWidgetTwo)
  
  

});



