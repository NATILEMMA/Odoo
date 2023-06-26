odoo.define('init_web_view_metadata.FormController', function (require) {
    "use strict";
    var FormController = require('web.FormController');
    var field_utils = require('web.field_utils');
    var Dialog = require('web.Dialog');
    var Sidebar = require('web.Sidebar');
    var core = require('web.core');

    var _t = core._t;
    var QWeb = core.qweb;

    FormController.include({
        renderSidebar: function ($node) {
            var self = this;
            if (this.hasSidebar) {
                var otherItems = [];
                if (this.archiveEnabled && this.initialState.data.active !== undefined) {
                    var classname = "o_sidebar_item_archive" + (this.initialState.data.active ? "" : " o_hidden")
                    otherItems.push({
                        label: _t("Archive"),
                        callback: function () {
                            Dialog.confirm(self, _t("Are you sure that you want to archive this record?"), {
                                confirm_callback: self._toggleArchiveState.bind(self, true),
                            });
                        },
                        classname: classname,
                    });
                    classname = "o_sidebar_item_unarchive" + (this.initialState.data.active ? " o_hidden" : "")
                    otherItems.push({
                        label: _t("Unarchive"),
                        callback: this._toggleArchiveState.bind(this, false),
                        classname: classname,
                    });
                }
                if (this.is_action_enabled('delete')) {
                    otherItems.push({
                        label: _t('Delete'),
                        callback: this._onDeleteRecord.bind(this),
                    });
                }
                if (this.is_action_enabled('create') && this.is_action_enabled('duplicate')) {
                    otherItems.push({
                        label: _t('Duplicate'),
                        callback: this._onDuplicateRecord.bind(this),
                    });
                }
                otherItems.push({
                    label: _t("View Metadata"),
                    callback: this._onShowViewMetaData.bind(this)
                });
                this.sidebar = new Sidebar(this, {
                    editable: this.is_action_enabled('edit'),
                    viewType: 'form',
                    env: {
                        context: this.model.get(this.handle).getContext(),
                        activeIds: this.getSelectedIds(),
                        model: this.modelName,
                    },
                    actions: _.extend(this.toolbarActions, {other: otherItems}),
                });
                return this.sidebar.appendTo($node).then(function() {
                     // Show or hide the sidebar according to the view mode
                    self._updateSidebar();
                });
            }
            return Promise.resolve();
        },
        _onShowViewMetaData: function () {
            var self = this;
            var active_ids = this.getSelectedIds();
            if (active_ids.length == 1) {
                this._rpc({
                    model: this.modelName,
                    method: 'get_metadata',
                    args: [active_ids],
                }).then(function(result) {
                    var metadata = result[0];
                    metadata.creator = field_utils.format.many2one(metadata.create_uid);
                    metadata.lastModifiedBy = field_utils.format.many2one(metadata.write_uid);
                    var createDate = field_utils.parse.datetime(metadata.create_date);
                    metadata.create_date = field_utils.format.datetime(createDate);
                    var modificationDate = field_utils.parse.datetime(metadata.write_date);
                    metadata.write_date = field_utils.format.datetime(modificationDate);
                    var dialog = new Dialog(this, {
                        title: _.str.sprintf(_t("View Metadata (%s)"), self.modelName),
                        size: 'medium',
                        $content: QWeb.render('WebClient.DebugViewLog', {
                            perm : metadata,
                        })
                    });
                    dialog.open().opened(function () {
                        dialog.$el.on('click', 'a[data-action="toggle_noupdate"]', function (ev) {
                            ev.preventDefault();
                            self._rpc({
                                model: 'ir.model.data',
                                method: 'toggle_noupdate',
                                args: [self._action.res_model, metadata.id]
                            }).then(function (res) {
                                dialog.close();
                                self.get_metadata();
                            })
                        });
                    });
                });
            }
        },

    });

});
