/** @odoo-module */
import { Message } from "@mail/core/common/message";
import { patch } from "@web/core/utils/patch";


patch(Message.prototype, {
    get canReplyTo() {
        if (this.props.message?.is_note)
            return false
        return super.canReplyTo;
    }
});
