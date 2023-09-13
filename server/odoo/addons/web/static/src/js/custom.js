

// odoo.define(function (require) {
//     "use strict";
    
//     var fieldRegistry = require('web.field_registry');
//     var AbstractField = require('web.AbstractField');
//     console.log("neeeeeeeeeeeeeeeeeee reloaded")
//     var Inputvalue = $('#test1').val();
//     console.log(" reloaded",Inputvalue)
    
//     var MyCustomField = AbstractField.extend({
//         _onFieldChange: function () {

            
//     console.log("hhhhhhhhhhhhhhh reloaded")

//     var Inputvalue = $('#popupDatepicker').val();

//             // your onchange function logic here
//             function checkField(){
//                 var temp = document.getElementById('test1').value;
//                 console.log("RRRRRRRRRRRRRRRRRR",temp)
//                 }
//         }
//     });
    
//     fieldRegistry.add('my_custom_field', MyCustomField);
    
//     return {
//         MyCustomField: MyCustomField
//     };
// });


odoo.define(function (require) {
    "use strict";
    console.log("rrrrrrrrrrrrRRRRRRRRRRRRRRRRRRRR reloaded")

    var basicFields = require('web.basic_fields');
    var FieldChar = basicFields.FieldChar;
    var core = require('web.core');

    var Widget = require('web.Widget');


            function checkField(){
                        var temp = document.getElementById('test1').value;
                        console.log("RRRRRRRRRRRRRRRRRR",temp)
                        
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
                        
                        }
});


odoo.define(function(require) {
    "use strict";
    var session = require('web.session');
    var rpc = require('web.rpc')
    var Widget = require('web.Widget');
    
    var current_url = window.location.href;
    var myArray = current_url.split("&");
    var current_model = myArray[2].replace('model=',''); 
    // var publicWidget = require('web.public.widget');
    const {_t, qweb} = require('web.core');
    console.log("LLLLLLLLLLLLLLLLL reloaded")

    var test = Widget.extend({
        selector: '.o_calendar_buttons',

        
        events:{},
    
    start: function() {
    // publicWidget.registry.test = publicWidget.Widget.extend({

    //     selector: '.o_calendar_buttons',
    //     read_events: {
    //         'change select[name="transfer_as_a_leader_or_member"]': '_transferChange',
    //     },

        
    //     start: function () {
    console.log("kkkkkkkkkkkkkkkk reloaded")

    function onChangeFunctionName(event) {
        var fieldValue = event.target.value;
        // Function code here
    console.log("rrrrrrrrrrrrRRRRRRRRRRRRRRRRRRRR reloaded")
    console.log("rrrrrrrrrrrrRRRRRRRRRRRRRRRRRRRR reloaded")
        
        // Update the view
        var widget = event.target.widgets[0];
        widget.do_some_action();
     }

            var def = this._super.apply(this, arguments);
            return def;
        },

    // function my_custom_field(){
    //     var temp = document.getElementById('test1').value;
    //     console.log("RRRRRRRRRRRRRRRRRR",temp)
        
    //     var res = rpc.query({
    //         model: model[0],
    //         method: 'date_convert_and_set',
    //         args: [pickeddate],
    //         }).then(function (data)
    //             {
    //             console.log("Response of payment",data)
    //             // console.log("Refresh...1111111111111111")

    //             // $("#popupDatepicker" ).datepicker("refresh");
    //         });
        
    //     }

    });

    
   
    // $('#popupDatepicker').load(location.href + ' #popupDatepicker');
    // $("#popupDatepicker" ).datepicker("refresh");

 
});