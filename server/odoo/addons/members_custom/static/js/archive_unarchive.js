odoo.define('module_name.BasicView', function (require) {

    "use strict";
    
    var session = require('web.session');
    
    var BasicView = require('web.BasicView');
    
    BasicView.include({
    
        init: function(viewInfo, params) {
    
          var self = this;
    
          this._super.apply(this, arguments);
    
          var model = self.controllerParams.modelName in ['supporter.members','donors', 'candidate.members'] ? 'True' : 'False';
    
          if(model === 'True') {
    
                self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                self.controllerParams.unarchiveEnabled = 'False' in viewInfo.fields;
    
            }
    
        },
    
    });
    
});