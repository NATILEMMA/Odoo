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
var EthiopianCalendarWidgetThree = Widget.extend({
  template: 'ethiopian_calander_widget_three',
  
  events:{},

start: function() {
  console.log("##### Ethiopian Calander Widget Three####")
  var def = new $.Deferred();
  let picked_date = [];
  let clicked_val = [];
  this._super();
  // this.$input = this.$('input.o_datepicker_input');
  var self = this;
  // console.log("This",this)
  var updateFormViewField3 = {
      dataPointID: this.getParent().__parentedParent.initialState.id,
      // changes: {'ethiopian_from': '2000-01-02'},
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
          "pick": 3,
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
          var dateThree =  (data.three).length
          console.log("threeeeeeeeeee", data.three)
          if(dateThree > 0){
              console.log("**** Both True")
              var  date3 = data['three'].toString()
              date3 = data['three'].split("-")

              if (date3[1] === undefined){
                var date33 = data['three'].split("/")
                var dateThree = date33[0] + "/" +  date33[1] + "/" +  date33[2]
                var dateThree = date33[0] + "/" + date33[1] + "/" +  date33[2]
                $("#DatepickerThree").val(dateThree);
              localStorage.setItem('myFlag_3', dateThree);

             }else{
              var dateThree = date1[1] + "/" +  date1[2] + "/" +  date1[0]
              //console.log(" From GGGGGG date:",date1)
              $("#DatepickerThree").val(dateThree);
              localStorage.setItem('myFlag_3', data['three']);
             }
          }else{
                  //console.log("--- Both False")
                  var  date = data.toString()
                  date = date.split("-")
                  var dates = date[1] + "/" +  date[2] + "/" +  date[0]
                  initial_date.push(dates)
                  var myFlag_3 = localStorage.getItem('myFlag_3');
                  console.log("intial 1", myFlag_3)
                 $("#DatepickerThree").val(dates);
                 // $("#DatepickerTwo").val(dates);
                  localStorage.setItem('myFlag_3', date);
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
   
      $('#DatepickerThree').calendarsPicker({calendar: calendar,onSelect:function()
      {
        console.log("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
        var dateObject = $(this).calendarsPicker("getDate")
        //console.log("dateObject", dateObject)
          let pickeddate = {
                  "day" : dateObject[0]._day,
                  "month" : dateObject[0]._month,
                  "year":dateObject[0]._year,
                  "current_model": current_model,
                  "url": current_url,
                  "pick": 3,
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
  var Inputvalue3 = $('#DatepickerThree').val();
  if(Inputvalue3 != null){
  if(parseInt(Inputvalue3.length) > 1){
  var Inputvalue3 = $('#DatepickerThree').val();
      Inputvalue3 = Inputvalue3.split("/")
      var value =  Inputvalue3[2]+'-'+Inputvalue3[0]+'-'+Inputvalue3[1]
      var updateFormViewField_3 = {
          dataPointID: updateFormViewField3.dataPointID,
          changes: {'ethiopian_three': value},
        }
      var myFlag_3 = localStorage.getItem('myFlag_3');
        console.log('flag..^^^^^^^^^^^', myFlag_3,value);
        if (myFlag_3 != value){
               console.log('has differncr',myFlag_3,value);
               localStorage.setItem('myFlag_3', value);
               var myFlag_3 = localStorage.getItem('myFlag_3');
               console.log('updateFormViewField_3',value);
               return this.trigger_up('field_changed', updateFormViewField_3);
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

widget_registry.add('ethiopian_calander_widget_three', EthiopianCalendarWidgetThree)
});



