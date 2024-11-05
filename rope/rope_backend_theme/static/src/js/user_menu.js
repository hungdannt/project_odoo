/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { preferencesItem } from '@web/webclient/user_menu/user_menu_items';
import { patch } from "@web/core/utils/patch";

patch(UserMenu.prototype,'web/static/src/webclient/user_menu/user_menu.js',{
    elementMenuClick(element){
        if (element.href) browser.open(element.href, "_blank");
        else if (element.callback) element.callback()
    }
});

registry.category("user_menuitems").remove("separator")
registry.category("user_menuitems").remove("log_out")
