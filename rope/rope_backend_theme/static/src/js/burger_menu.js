/** @odoo-module **/

import { BurgerMenu } from "@web_enterprise/webclient/burger_menu/burger_menu";
import { patch } from "@web/core/utils/patch";
const { useExternalListener } = owl.hooks;
const { Component } = owl;


patch(BurgerMenu.prototype, 'rope_backend_theme', {
    setup(){
        this._super(...arguments);
        useExternalListener(window, "click", (ev) =>{
            if(ev.target.className.includes('menu_item')){
                let id = $(ev.target).attr('action-id')
                Component.env.bus.trigger('menuitem_click', {menu_id: id})
            }
        });
        window.menuItemIns = this
        Component.env.bus.on('menuitem_click', this, (data) => {
            if(window.menuItemIns.currentAppSections.length){
                let menuItem = window.menuItemIns._getMenuItem(data.menu_id, window.menuItemIns.currentAppSections)
                if(menuItem){
                    window.menuItemIns._onMenuClicked(menuItem)
                }
            }
        })
    },
    _getMenuItem(id, menus){
        let allMenus = window.menuItemIns._getAllMenu([], menus)
        let res = allMenus.filter((e)=>{
            return e.id == id
        })

        return res[0]
    },
    _getAllMenu(allMenus, menus){
        for(let menu of menus){
            allMenus.push(menu)
            if(menu.childrenTree.length){
                window.menuItemIns._getAllMenu(allMenus, menu.childrenTree)
            }
        }
        return allMenus
    }
})