/** @odoo-module **/

import { FileViewer } from "@web/core/file_viewer/file_viewer";
import { onWillDestroy, onMounted } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

patch(FileViewer.prototype, {

    setup(){
        super.setup();
        onMounted(() => {
            this.dialogs = $('.o_dialog')
            if(this.dialogs)
                this.dialogs.addClass('d-none')

          });
        onWillDestroy(() => {
            if(this.dialogs)
                this.dialogs.removeClass('d-none')
          });
    }
});
