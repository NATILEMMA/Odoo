/*************************************************************************************************
*
* Author    => Albertus Restiyanto Pramayudha
* email     => xabre0010@gmail.com
* linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
* youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
*
*************************************************************************************************/
odoo.define('hide_button_candidate_js.in_candidate_list_view', function (require) {
    "use strict";

    var ListController = require('web.ListController');

    ListController.include({
         renderButtons: function($node) {
             this._super.apply(this, arguments);
             if (this.modelName =='candidate.members') {
                var create_button = $(this.$buttons.find('.o_list_button_add'));
                create_button.css({"display":"none"});
                var import_button = $(this.$buttons.find('.o_button_import'));
                import_button.css({"display":"block"});
             }
          }
      });

      var Menus = new openerp.web.Model('ir.model.data');
      Menus.query(['name']).filter([['model', '=', 'res.partner']]).all().then(function(ir_model_datas) {
         for (i in ir_model_datas) {
            console.log(ir_model_datas[i].name);
         }
      });

});