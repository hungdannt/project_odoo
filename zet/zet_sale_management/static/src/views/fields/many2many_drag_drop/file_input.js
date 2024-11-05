/** @odoo-module */
import { useBus } from "@web/core/utils/hooks";
import { FileInput } from "@web/core/file_input/file_input";
import { patch } from "@web/core/utils/patch";

patch(FileInput.prototype, {
    setup(){
        super.setup();
        useBus(this.env.bus, "ZET:CHANGE_FILES_INPUT_DRAG_DROP", async (ev) => {
            this.fileInputRef.el.files = ev.detail.files;
            await this.onFileInputChange();
        }); 
    }
});
