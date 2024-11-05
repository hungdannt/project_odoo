/** @odoo-module **/
import { _t } from "@web/core/l10n/translation";
import { useFileViewer } from "@web/core/file_viewer/file_viewer_hook";
import { useRef, onWillDestroy , onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";
import { Many2ManyBinaryField, many2ManyBinaryField } from "@web/views/fields/many2many_binary/many2many_binary_field"

export class Many2ManyDragDrop extends Many2ManyBinaryField {
    setup(){
        super.setup()
        this.dialogService = useService("dialog");
        this.upload_file_drag_drop = useRef("upload_file_drag_drop");
        onMounted(this.addEventListenerInUploadFile);
        onWillDestroy(this.removeListenerInUploadFile);
        this.fileViewer = useFileViewer();
    }

    addEventListenerInUploadFile(){
        this.upload_file_drag_drop.el.addEventListener("dragover", this.highlight.bind(this));
        this.upload_file_drag_drop.el.addEventListener("dragleave", this.unhighlight.bind(this));
        this.upload_file_drag_drop.el.addEventListener("drop", this.onDrop.bind(this));
    }

    removeListenerInUploadFile(){
        this.upload_file_drag_drop.el.removeEventListener("dragover", this.highlight.bind(this));
        this.upload_file_drag_drop.el.removeEventListener("dragleave", this.unhighlight.bind(this));
        this.upload_file_drag_drop.el.removeEventListener("drop", this.onDrop.bind(this));
    }

    highlight(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        this.upload_file_drag_drop.el.classList.add('drag_over');
    }

    unhighlight(ev) {
        ev.stopPropagation();
        ev.preventDefault();
        this.upload_file_drag_drop.el.classList.remove('drag_over');
    }

    async onDrop(ev) {
        ev.preventDefault();
        await this.env.bus.trigger("ZET:CHANGE_FILES_INPUT_DRAG_DROP", {
            files: ev.dataTransfer.files,
        });     
        this.upload_file_drag_drop.el.classList.remove('drag_over');
    }

    get files() {
        const self = this
        return this.props.record.data[this.props.name].records.map((record) => {
            const isText = true ? record.data.mimetype.indexOf('text') !== -1: false
            const isPdf = true ? record.data.mimetype.indexOf('pdf') !== -1: false
            const isImage = true ? record.data.mimetype.indexOf('image') !== -1: false
            const isVideo = true ? record.data.mimetype.indexOf('video') !== -1: false
            return {
                ...record.data,
                id: record.resId,
                displayName: record.data.name,
                isText: isText,
                isPdf:isPdf,
                isImage: isImage,
                isVideo: isVideo,
                isViewable:true ? isText || isPdf || isImage || isVideo : false,
                defaultSource: self.getUrl(record.resId).replace('?download=true', '')
            }
        });
    }

    async onFileRemove(deleteId) {
        const dialogProps = {
            body: _t(
                "Are you sure you want to delete this attachment? This action cannot be undone."
            ),
            confirm: () => super.onFileRemove(deleteId),
            cancel: () => {},
        };
        this.dialogService.add(ConfirmationDialog, dialogProps);
    }
}

Many2ManyDragDrop.template = 'zet_sale_management.Many2ManyDragDrop'

export const many2ManyDragDrop = { ...many2ManyBinaryField, component: Many2ManyDragDrop}

registry.category("fields").add("many2many_drag_drop", many2ManyDragDrop);
