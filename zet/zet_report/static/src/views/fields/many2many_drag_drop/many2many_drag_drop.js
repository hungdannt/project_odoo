/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Many2ManyDragDrop, many2ManyDragDrop } from "@zet_sale_management/views/fields/many2many_drag_drop/many2many_drag_drop"

export class Many2ManyDragDropPrint extends Many2ManyDragDrop {
    onChangeSelectPrint(file) {
        this.orm.write('ir.attachment', [file.id], { is_printed: !file.is_printed});
    }
}

Many2ManyDragDrop.template = 'zet_report.Many2ManyDragDropPrint'

export const many2ManyDragDropPrint = { ...many2ManyDragDrop, component: Many2ManyDragDropPrint, relatedFields: [
    { name: "name", type: "char" },
    { name: "mimetype", type: "char" },
    { name: "is_printed", type: "boolean" },
] };
registry.category("fields").add("many2many_drag_drop_print", many2ManyDragDropPrint);



