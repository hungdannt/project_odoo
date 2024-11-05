/** @odoo-module **/

import { WebClientEnterprise } from "@web_enterprise/webclient/webclient";
import { patch } from "@web/core/utils/patch";

patch(WebClientEnterprise.prototype,'rope_backend_theme',{
    _updateClassList(){
        this.el.classList.toggle("o_home_menu_background", this.hm.hasHomeMenu);
        this.el.classList.toggle("o_has_home_menu", this.hm.hasHomeMenu);
        $('.sidebar__content__menu-item')[0].classList.toggle("d-none", this.hm.hasHomeMenu);
        $('.sidebar__header__menu-name')[0].classList.toggle("d-none", this.hm.hasHomeMenu);
        $('.sidebar__header__menu')[0].classList.toggle("d-none", this.hm.hasHomeMenu);
        $('.sidebar__content__home')[0].classList.toggle("d-none", this.hm.hasHomeMenu);
        $('.sidebar__header__company').toggleClass("d-none");
        $('.sidebar__content__padding').toggleClass("d-none");
    }
});
