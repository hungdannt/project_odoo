odoo.define('rope_sale.FormController', function (require) {
"use strict";

    var FormController = require('web.FormController');

    var FormController = FormController.include({
        _discardChanges: async function () {
            var res = this._super(...arguments)
            await this._discardDuplicateRecord()
            return res
        },

        _discardDuplicateRecord: async function(){
            var record = this.model.get(this.handle);
            if (this.modelName == 'sale.order' && record.data.id){
                let ids = [this.handle]
                let isDuplicateRec = await this._rpc({
                    method: 'check_is_duplicate_record',
                    model: 'sale.order',
                    args: [record.data.id],
                })
                if(isDuplicateRec){
                    this.model.deleteRecords(ids, this.modelName).then(this._onUpdateRecords.bind(this, ids));
                }
            };
        },

        saveRecord: async function () {
            const changedFields = await this._super(...arguments);
            var self = this;
            var record = this.model.get(this.handle);
            let id = this['model'].loadParams.res_id;
            // validate model and res_id
            if (this.modelName == 'sale.order' && id){
                this._rpc({
                    method: 'write',
                    model: 'sale.order',
                    args: [id, {'is_duplicate_record': false}],
                    context: self.model.loadParams.context,
                }).then(res => {
                    self._onUpdateRecords.bind(self, [self.handle])
                });
            }
            return changedFields;
        },

        _onUpdateRecords: function (ids) {
            this.update({});
        },

        update: async function (params, options) {
            this.mode = params.mode || this.mode;
            return this._super(params, options);
        },
    });
    return FormController
});
