/* @odoo-module */

import { prettifyMessageContent } from "@mail/utils/common/format";

import { Composer } from "@mail/core/common/composer";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(Composer.prototype, {

    async _sendMessage(value, postData) {
        const { threadSelect, isReplyAll } = this.props;
        if (threadSelect?.message) {
            const { message } = threadSelect;
            this.thread.subject = message.subject;
            if (!isReplyAll) {
                this.thread.partner = message.author?.id;
            }
            threadSelect.obj?.cancel();
        }
        await super._sendMessage(value, postData);
    },

    async onClickFullComposer(ev) {
        if (this.props.type !== "note") {
            // auto-create partners of checked suggested partners
            const newPartners = this.thread.suggestedRecipients.filter(
                (recipient) => recipient.checked && !recipient.persona
            );
            if (newPartners.length !== 0) {
                const recipientEmails = [];
                const recipientAdditionalValues = {};
                newPartners.forEach((recipient) => {
                    recipientEmails.push(recipient.email);
                    recipientAdditionalValues[recipient.email] =
                        recipient.defaultCreateValues || {};
                });
                const partners = await this.rpc("/mail/partner/from_email", {
                    emails: recipientEmails,
                    additional_values: recipientAdditionalValues,
                });
                for (const index in partners) {
                    const partnerData = partners[index];
                    const persona = this.store.Persona.insert({ ...partnerData, type: "partner" });
                    const email = recipientEmails[index];
                    const recipient = this.thread.suggestedRecipients.find(
                        (recipient) => recipient.email === email
                    );
                    Object.assign(recipient, { persona });
                }
            }
        }
        const attachmentIds = this.props.composer.attachments.map((attachment) => attachment.id);
        const body = this.props.composer.textInputContent;
        const validMentions = this.store.user
            ? this.messageService.getMentionsFromText(body, {
                  mentionedChannels: this.props.composer.mentionedChannels,
                  mentionedPartners: this.props.composer.mentionedPartners,
              })
            : undefined;
        const context = {
            default_attachment_ids: attachmentIds,
            default_body: await prettifyMessageContent(body, validMentions),
            default_model: this.thread.model,
            default_partner_ids:
                this.props.type === "note"
                    ? []
                    : this.thread.suggestedRecipients
                          .filter((recipient) => recipient.checked)
                          .map((recipient) => recipient.persona.id),
            default_res_ids: [this.thread.id],
            default_subtype_xmlid: this.props.type === "note" ? "mail.mt_note" : "mail.mt_comment",
            mail_post_autofollow: this.thread.hasWriteAccess,
            subject: this.props?.threadSelect?.message?.subject
        };
        const action = {
            name: this.props.type === "note" ? _t("Log note") : _t("Compose Email"),
            type: "ir.actions.act_window",
            res_model: "mail.compose.message",
            view_mode: "form",
            views: [[false, "form"]],
            target: "new",
            context: context,
        };
        const options = {
            onClose: (...args) => {
                // args === [] : click on 'X'
                // args === { special: true } : click on 'discard'
                const isDiscard = args.length === 0 || args[0]?.special;
                // otherwise message is posted (args === [undefined])
                if (!isDiscard && this.props.composer.thread.type === "mailbox") {
                    this.notifySendFromMailbox();
                }
                this.clear();
                this.props.messageToReplyTo?.cancel();
                if (this.thread) {
                    this.threadService.fetchNewMessages(this.thread);
                }
            },
        };
        await this.env.services.action.doAction(action, options);
    }
});

Composer.props = {...Composer.props, "threadSelect?":null}
