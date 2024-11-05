/** @odoo-module */
import { SectionAndNoteListRenderer } from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend";
import {  onWillUpdateProps } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

patch(SectionAndNoteListRenderer.prototype, {
    setup(){
        super.setup();
        onWillUpdateProps(nextProps => {
            nextProps.list.records.sort((a, b) => {
                const aSeq = a.data?.sequence ?? Number.MAX_SAFE_INTEGER;
                const bSeq = b.data?.sequence ?? Number.MAX_SAFE_INTEGER;
                return aSeq - bSeq;
              });
        });
    },

    getRowClass(record) {
        const existingClasses = super.getRowClass(record);
        if (record.data.display_type === 'line_section' && !record.data.is_sub_section)
            return `${existingClasses} text-decoration-underline`;
        else if (record.data.display_type === 'line_section' && record.data.is_sub_section)
            return `${existingClasses} is_sub_section`;
        return existingClasses
    }
});
