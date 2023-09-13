/*************************************************************************************************
*
* Author    => Albertus Restiyanto Pramayudha
* email     => xabre0010@gmail.com
* linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
* youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA
*
*************************************************************************************************/
odoo.define('hide_button_candidate_js.in_candidate_kanban', function (require) {
    "use strict";

        var KanbanController = require('web.KanbanController');

        KanbanController.include({
            renderButtons: function ($node) {
                 this._super.apply(this, arguments);
                 if (this.modelName =='candidate.members') {
                    var create_button = $(this.$buttons.find('.o-kanban-button-new'));
                    create_button.css({"display":"none"});
                    var import_button = $(this.$buttons.find('.o_button_import'));
                    import_button.css({"display":"block"});
                 }
            }
        });
});