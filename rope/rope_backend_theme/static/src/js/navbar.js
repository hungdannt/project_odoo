/** @odoo-module **/

import { useEffect, useService, onDestroyed } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { debounce } from "@web/core/utils/timing";
import { browser } from "@web/core/browser/browser";
import { NavBar } from "@web/webclient/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useEnvDebugContext } from "@web/core/debug/debug_context";

const { Component } = owl;
const { useExternalListener, useRef, onWillUnmount } = owl.hooks;
const systrayRegistry = registry.category("systray");

patch(NavBar.prototype,'web/static/src/webclient/navbar/navbar.js',{

    setup() {
        this.debug = this.env.debug
        this.debugContext = useEnvDebugContext();
        this.currentAppSectionsExtra = [];
        this.actionService = useService("action");
        this.menuService = useService("menu");
        this.appSubMenus = useRef("appSubMenus");
        const debouncedAdapt = debounce(this.adapt.bind(this), 250);
        onDestroyed(() => debouncedAdapt.cancel());
        useExternalListener(window, "resize", debouncedAdapt);
        this.user = useService("user");
        const { origin } = browser.location;
        const { userId } = this.user;
        this.source = `${origin}/web/image?model=res.users&field=avatar_128&id=${userId}`;
        let adaptCounter = 0;
        const renderAndAdapt = () => {
            adaptCounter++;
            this.render();
            Component.env.bus.trigger('systray_get_activities')
        };
        Component.env.bus.on('activity_updated', this, renderAndAdapt);

        systrayRegistry.on("UPDATE", this, renderAndAdapt);
        this.env.bus.on("MENUS:APP-CHANGED", this, renderAndAdapt);

        onWillUnmount(() => {
            systrayRegistry.off("UPDATE", this);
            this.env.bus.off("MENUS:APP-CHANGED", this);
        });
        useEffect(() => {this.adapt();}, () => [adaptCounter]);
    },

    get systrayItems() {
        return systrayRegistry
            .getEntries()
            .map(([key, value]) => ({ key, ...value }))
            .reverse();
    },

    async getElementsDebug(elementDebug){
        elementDebug.empty()
        let listItemDebug = document.createElement('div');
        let elements = await this.debugContext.getItems(this.env);
        for(let item of elements){
            if(item.type === 'item'){
                let li = document.createElement('li')
                let span = document.createElement('span')
                span.innerHTML = item.description
                span.onclick = item.callback
                li.append(span)
                li.append(document.createElement('hr'))
                listItemDebug.append(li)
            }
        }
        elementDebug.append(listItemDebug)
    },

    async toggleListItemDebug(ev){
        if($('.o_debug_manager_custom.open').length){
            $(ev.target).closest('.o_debug_manager_custom').removeClass('open')
        }else{
            $(ev.target).closest('.o_debug_manager_custom').addClass('open')
        }

        let elementDebug = $('.o_debug_manager_custom__item');
        let elementDebugRight = $('.o_debug_manager_custom__right-icon');
        elementDebug.toggleClass('d-none');
        elementDebugRight.toggleClass('d-none');
        await this.getElementsDebug(elementDebug);
    },
});
