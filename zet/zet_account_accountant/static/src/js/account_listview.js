/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { AccountDashBoard } from '@zet_account_accountant/js/account_dashboard';

export class AccountDashBoardRenderer extends ListRenderer {};

AccountDashBoardRenderer.template = 'zet_account_accountant.accountListView';
AccountDashBoardRenderer.components= Object.assign({}, ListRenderer.components, {AccountDashBoard})

export const AccountDashBoardListView = {
    ...listView,
    Renderer: AccountDashBoardRenderer,
};

registry.category("views").add("account_dashboard_list", AccountDashBoardListView);
