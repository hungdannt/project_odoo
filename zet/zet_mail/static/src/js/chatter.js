/* @odoo-module */

import { Chatter } from "@mail/core/web/chatter";
import { patch } from "@web/core/utils/patch";
import { useState, useExternalListener, onWillStart } from "@odoo/owl";
import { browser } from "@web/core/browser/browser";

patch(Chatter.prototype, {

    setup() {
        super.setup();
        this.messageToReplyTo = this.useMessageToReplyTo();
        this.threadSelect = {}
        this.state = useState({
            ...this.state,
            showButtonsReplyAll: false,
            isReplyAll: true
        })
        onWillStart(async () => {
            this.hasFetchEmail = await this.orm.call("fetchmail.server", "get_show_button_fetch_email", [], {}) && this.env?.model?.config?.resModel === 'sale.order';
        });
        useExternalListener(browser, "keyup", this._onKeyUp, { capture: true });
    },
    
    _onKeyUp(ev) {
        if (ev.key === 'Escape'){
            this.state.showButtonsReplyAll = false
            this.state.isReplyAll = true
            this.messageToReplyTo.cancel()
            this.toggleComposer()
        }
    },

    async onFetchEmailIncomingMailServers(){
        await this.orm.call("fetchmail.server", "fetch_mails", [], {});
        await this.reloadParentView()
    },

    onChangeReplyAllInput(ev){
        this.state.isReplyAll = ev.target.checked
    },

    get toRecipientsText() {
        if (this.state.isReplyAll){
            return super.toRecipientsText
        }else{
            return this.threadSelect.message.author.email.split('@')[0];
        }
    },

    onClickRecipientList(ev) {
        const { recipientsPopover, threadSelect, state } = this;
        if (recipientsPopover.isOpen) {
            return recipientsPopover.close();
        }
        const { message } = threadSelect || {};
        if (message && !this.state.isReplyAll) {
            const { author, recipients } = message;
            recipients[0].partner = author;
            message.recipientsFullyLoaded = true;
            recipientsPopover.open(ev.target, { thread: message });
        } else {
            recipientsPopover.open(ev.target, { thread: state.thread });
        }
    },

    useMessageToReplyTo(){
        const self = this
        return useState({
            cancel() {
                self.threadSelect = {}
                Object.assign(this, { message: null, thread: null });
            },
           
            isNotSelected(thread, message) {
                return thread.eq(this.thread) && message.notEq(this.message);
            },
            
            isSelected(thread, message) {
                return thread.eq(this.thread) && message.eq(this.message);
            },
           
            toggle(thread, message) {
                if(message.is_note)
                    return
                self.threadSelect = {}
                self.toggleComposer()
                if (message.eq(this.message)) {
                    this.cancel();
                } else {
                    Object.assign(this, { message, thread });
                    self.threadSelect.message = message
                    self.state.isReplyAll = false
                    self.state.showButtonsReplyAll = true
                    self.threadSelect.obj = this
                    self.toggleComposer('message')
                }
            },
        });
    }
});
