
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
  // console.log("##########",this.$input)
  var self = this;

  console.log("This",this)
  var updateFormViewField1 = {
      dataPointID: this.getParent().__parentedParent.initialState.id,
      changes: {'ethiopian_from': '2000-01-02'},
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
          "pick": 1,
      }
                     

     
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
      //                 $("#popupDatepicker").val('01/01/2020');
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

      //                     $("#popupDatepicker").val('01/01/2020');
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
   
      $('#DatepickerTwo').calendarsPicker({calendar: calendar,onSelect:function()
      {
        var dateObject = $(this).calendarsPicker("getDate")
        console.log("dateObject", dateObject)
      //     let pickeddate = {
      //             "day" : dateObject[0]._day,
      //             "month" : dateObject[0]._month,
      //             "year":dateObject[0]._year,
      //             "current_model": current_model,
      //             "url": current_url,
      //             "pick": 1,

      //             }

      //   var dd,model;
      //   console.log("Picked:",pickeddate)
      //   let val = 0
      //   var updateFormViewField = {
      //     dataPointID: updateFormViewField1.dataPointID,
      //     changes: {'ethiopian_from': '2015-01-02'},
      //   }
      //   console.log("updateFormViewField_34", updateFormViewField)

      //   console.log("if con",callTrigger)
      //   callTrigger('field_changed', updateFormViewField);
//                break;
          // trigger_up: function(name, info) {
          //     var event = new OdooEvent(this,name,info);
          //     this._trigger_up(event);
          //     return event;
        // console.log("KKKKKKpickeddate",pickeddate)

      //   dd = current_url.split('model=')
      //   model = dd[1].toString()
      //   model = model.split('&')
      //   console.log("############ id",model)
      //   console.log("############ Model",model[0])
      //   var res = rpc.query({
      //             model: model[0],
      //             method: 'date_convert_and_set',
      //             args: [pickeddate],
      //         }).then(function (data)
      //         {
      //         console.log("Response of payment",data)
      //         // console.log("Refresh...1111111111111111")

      //         // $("#DatepickerTwo" ).datepicker("refresh");
      //     });
              // then(function(data){
              //   console.log("rrrrrrrrrr",data)
              //   if (data['reload'] == True){
              //     window.setTimeout(function(){ document.location.reload(true); }, 15000);
              //   }
                  
             
          //    });
      //     clicked_val.push('1')
      // $("#DatepickerTwo" ).datepicker("refresh");
      // this.saveDate()
      // location.reload(true);
      // window.location.reload();
      // $('#DatepickerTwo').load(location.href + ' #DatepickerTwo');
      // odoo.reload();
  //     if ($datePicker.length) {
  //       console.log("###############################")
  //       $datePicker.datepicker('refresh');
  //   }
      }});

      
  });
   

      var Inputvalue = $('#DatepickerTwo').val();
      console.log("AAAAAAAAAAAAA after",Inputvalue)
      // console.log("AAAAAAAAAAAAA afterlllllll",Inputvalue.length)
      // console.log("AAAAAAAAAAAAA afterlllllll",(Inputvalue.length))

      if(Inputvalue != null){
      if(parseInt(Inputvalue.length) > 1){

          console.log("KKclicked_val",clicked_val)
      var Inputvalue = $('#DatepickerTwo').val();
      console.log("V  before",Inputvalue)

          Inputvalue = Inputvalue.split("/")
          var value =  Inputvalue[2]+'-'+Inputvalue[0]+'-'+Inputvalue[1]
               console.log("value",value)
               
          var updateFormViewField = {
              dataPointID: updateFormViewField1.dataPointID,
              changes: {'ethiopian_from': value},
            }
          return this.trigger_up('field_changed', updateFormViewField);


      }
      else{
          console.log("FFFFFFFFFFFFFFFFFFFF")
          // $("#DatepickerTwo").val('01/01/2020');
          // $("#DatepickerTwo").val('01/01/2020');

      }
  }

  async function saveDate(){


  }

   
},



});

widget_registry.add('ethiopian_calander_widget_two', EthiopianCalendarWidgetTwo)

