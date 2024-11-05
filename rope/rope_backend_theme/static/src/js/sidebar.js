odoo.define('rope_backend_theme.SideBar', function (require) {
    "use strict";
    $(document).on("click", function(ev){
        if(!ev.target.className.includes('o_debug_manager') && $('.o_debug_manager_custom.open').length){
            $('.o_debug_manager_custom.open').removeClass('open')
            $('.o_debug_manager_custom__item').toggleClass('d-none');
            $('.o_debug_manager_custom__right-icon').toggleClass('d-none');
        }
    })

    $(document).on("click", ".sidebar__header__menu", function(event){
        if ($(window).width() > 680){
            $(".sidebar").css({'width':'90px','transition':'all 0.2s linear'});
            $(".o_action_manager_padding_left").css({'left': '90px','transition':'all 0.2s linear'});
            $(".o_action_manager_padding_left").css({'width': '60px'});
            $(".o_action_manager_padding_right").css({'width': '60px','transition':'all 0.2s linear'});
            $(".o_action_manager").css({'margin-left': '150px','margin-right':'60px','transition':'all 0.2s linear'});
            $(".o_action_manager_padding_top").css({'left': '90px','transition':'all 0.2s linear'});
            $(".o_action_manager_padding_bottom").css({'left': '90px','transition':'all 0.2s linear'});
            $(".sidebar__header").css({'padding': '55px 0 44px 0','justify-content':'center','transition':'all 0.2s linear'});
            $(".sidebar__content__home").css({'margin': '0px 18px 0px 18px','transition':'all 0.2s linear'});
            $(".sidebar__footer").css({'padding': '45px 22px 0px 17px','transition':'all 0.2s linear'});
            $(".sidebar__content__activity").css({'padding': '55px 21px 0px 15px','transition':'all 0.2s linear'});
            $(".sidebar__content__MessagingMenu").css({'margin': '330px 17px 0','transition':'all 0.2s linear'});
            $(".sidebar__footer__icon-logout").removeClass('d-none');
            $(".sidebar__collapse").hide();
            $(".sidebar__header__menu-name").hide();
            $(".sidebar__header__menu").addClass('open_sidebar');
            $(".sidebar__footer__user").addClass('open_sidebar');
            $(".sidebar__content__home").addClass('open_sidebar');
            $(".o_mail_systray_item__title").addClass('open_sidebar');
            $(".sidebar__content__menu-item").addClass('extend');
            $(".sidebar__content__menu-item").css({'display':'none','transition':'all 0.2s linear'});
            $(".sidebar__footer__menu-user").addClass('d-none');
            $(".sidebar__content__company").addClass('d-none');
            $(".sidebar__content__debug").addClass('d-none');
            $(".o_mail_systray_dropdown_items").addClass('d-none');
            $(".sidebar__content__MessagingMenu").addClass('open_sidebar');
        }
    });

    $(document).on("click", ".open_sidebar", function(event){
        $(".sidebar").css({'width':'32%','transition':'all 0.2s linear'});
        $(".o_action_manager").css({'margin-left': '35%','margin-right': '3%','transition':'all 0.2s linear'});
        $(".o_action_manager_padding_left").css({'left': '32%','transition':'all 0.2s linear'});
        $(".o_action_manager_padding_left").css({'width': '3%'});
        $(".o_action_manager_padding_right").css({'width': '3%','transition':'all 0.2s linear'});
        $(".o_action_manager_padding_top").css({'left': '35%','transition':'all 0.2s linear'});
        $(".o_action_manager_padding_bottom").css({'left': '35%','transition':'all 0.2s linear'});
        $(".sidebar__header").css({'padding': '55px 12% 44px 9%','justify-content':'space-between','transition':'all 0.2s linear'});
        $(".sidebar__content__home").css({'margin': '0px 12% 28px 9%','transition':'all 0.2s linear'});
        $(".sidebar__footer").css({'padding': '0px 12% 70px 9%','transition':'all 0.2s linear'});
        $(".sidebar__content__activity").css({'padding': '0px 12% 26px 9%','transition':'all 0.2s linear'});
        $(".sidebar__content__MessagingMenu").css({'margin': '0px 12% 28px 9%','transition':'all 0.2s linear'});
        $(".sidebar__header__menu-name").show();
        $(".sidebar__content__menu-item").css({'display':'block','transition':'all 0.2s linear'});
        $(".sidebar__footer__icon-logout").addClass('d-none');
        $(".sidebar__collapse").show();
        $(".sidebar__content__menu-item").removeClass('extend');
        $(".sidebar__footer__menu-user").removeClass('d-none');
        $(".open_sidebar").removeClass('open_sidebar');
        $(".sidebar__content__company").removeClass('d-none');
        $(".sidebar__content__debug").removeClass('d-none');
        $(".o_mail_systray_dropdown_items").removeClass('d-none');
    });

    $(document).on("click", ".o_MessagingMenu__title", function(event) {
        var messagingMenuList = $(".o_MessagingMenu__list");
        var messagingMenuIcon = $(".o_MessagingMenu__i");

        if (messagingMenuList.hasClass('d-none')) {
            messagingMenuList.removeClass('d-none');
            messagingMenuIcon.removeClass('fa-angle-right').addClass('fa-angle-down');
        } else {
            messagingMenuList.addClass('d-none');
            messagingMenuIcon.removeClass('fa-angle-down').addClass('fa-angle-right');
        }
    });

    const listTabId = ['all', 'chat', 'channel'];

    for (let tabId in listTabId) {
        $(document).on("click", ".o_MessagingMenu__tabBox_content--" + listTabId[tabId], function(event) {
            var notificationList = $(".notificationList--" + listTabId[tabId]);
            var o_MessagingMenu__i_active = $(".o_MessagingMenu__i_active--" + listTabId[tabId]);
            if (!notificationList.hasClass('d-none')) {
                notificationList.addClass('d-none');
                o_MessagingMenu__i_active.addClass('fa-angle-right');
                o_MessagingMenu__i_active.removeClass('fa-angle-down');
            } else {
                notificationList.removeClass('d-none');
                o_MessagingMenu__i_active.removeClass('fa-angle-right');
                o_MessagingMenu__i_active.addClass('fa-angle-down');
            }
        });
    }

    $(document).on("click", ".open_menu_item", function(event){
        let list_menu =  this.parentNode.getElementsByClassName('list_sub_menu')[0]
        if (list_menu){
            list_menu.classList.toggle('d-none')
            if ($(this).find('i').hasClass('fa-angle-down')){
                $(this).find('i').removeClass('fa-angle-down').addClass('fa-angle-right')
            }else{
                $(this).find('i').addClass('fa-angle-down').removeClass('fa-angle-right')
                }
        }
    })

    $(document).on("click", ".sidebar__footer__user", function(event){
        if (!$(".sidebar__footer__menu-user").hasClass('extend')){
            $(".sidebar__footer__menu-user").css({'display':'block'}).addClass('extend');
        }
        else if ($(".sidebar__footer__menu-user").hasClass('extend')){
            $(".sidebar__footer__menu-user").css({'display':'none'}).removeClass('extend')
        }

        if ($(".item-right").hasClass('fa-angle-right') && !$(".sidebar__footer__user").hasClass('extend')){
           $(".item-right").removeClass('fa-angle-right').addClass('fa-angle-down')
        }else if ($(".item-right").hasClass('fa-angle-down') && !$(".sidebar__footer__user").hasClass('extend')){
           $(".item-right").removeClass('fa-angle-down').addClass('fa-angle-right')
        }
    })

    $(document).on("click", ".o_switch_company_menu__title", function(event){
        if (!$(".o_switch_company_menu__footer").hasClass('extend')){
            $(".o_switch_company_menu__footer").css({'display':'block'}).addClass('extend') &&
            $(".o_switch_company_menu__list").css({'display':'block'})
        }
        else if ($(".o_switch_company_menu__footer").hasClass('extend')){
            $(".o_switch_company_menu__footer").css({'display':'none'}).removeClass('extend') &&
            $(".o_switch_company_menu__list").css({'display':'none'})
        }

        if ($(".item-right-company").hasClass('fa-angle-right')){
           $(".item-right-company").removeClass('fa-angle-right').addClass('fa-angle-down')
        }else if ($(".item-right-company").hasClass('fa-angle-down')){
           $(".item-right-company").removeClass('fa-angle-down').addClass('fa-angle-right')
        }
    })

    $(document).on("click", ".o_mail_systray_item__title", function(event){
        if (!$(".o_mail_systray_dropdown_items").hasClass('extend')){
            $(".o_mail_systray_dropdown_items").css({'display':'block'}).addClass('extend')
        }
        else if ($(".o_mail_systray_dropdown_items").hasClass('extend')){
            $(".o_mail_systray_dropdown_items").css({'display':'none'}).removeClass('extend')
        }
        if ($(".item-right-activity").hasClass('fa-angle-right')){
           $(".item-right-activity").removeClass('fa-angle-right').addClass('fa-angle-down')
        }else if ($(".item-right-activity").hasClass('fa-angle-down')){
           $(".item-right-activity").removeClass('fa-angle-down').addClass('fa-angle-right')
        }
    })

    $(document).on("click", ".sidebar__close_sidebar_mobile__icon", function(event){
        $(".sidebar").css({'margin-left':'-83%','transition':'all 0.3s linear'});
        $(".o_open_sidebar_mobile").css({'display': 'block'});
        $(".sidebar_backdrop").css({'display': 'none'});
    });

    $(document).on("click", ".o_open_sidebar_mobile__icon", function(event){
        $(".sidebar").css({'margin-left':'0%','transition':'all 0.3s linear'});
        $(".o_open_sidebar_mobile").css({'display': 'none'});
        $(".sidebar_backdrop").css({'display': 'block'});
    });

    $(document).on("click", ".sidebar__content__home__title", function(event){
        if ($(window).width() <= 680) {
            $(".sidebar").css({'margin-left':'-83%','transition':'all 0.3s linear'});
            $(".o_open_sidebar_mobile").css({'display': 'block'});
            $(".sidebar_backdrop").css({'display': 'none'});
        }
    });

});