/** @odoo-module */

import { ThreadService } from "@mail/core/common/thread_service";
import { patch } from "@web/core/utils/patch";

patch(ThreadService.prototype, {

    async getMessagePostParams({
        attachments,
        body,
        cannedResponseIds,
        isNote,
        mentionedChannels,
        mentionedPartners,
        thread,
    }){
        const res = await super.getMessagePostParams(...arguments)
        if (res.context)
            res.context.subject = thread.subject
            res.context.partner = thread.partner
        return res
    }
});
