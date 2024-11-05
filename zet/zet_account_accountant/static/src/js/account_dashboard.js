/** @odoo-module */
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, onWillUpdateProps, useState } from "@odoo/owl";

export class AccountDashBoard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            dataDasgBoard: {}
        })

        onWillStart(async () => {
            this.state.dataDasgBoard = await this.orm.call("account.move", "retrieve_dashboard", [this.props.domain], {
                context: this.props.context})
        });
        onWillUpdateProps(async (nextProps) => {
            this.state.dataDasgBoard = await this.orm.call("account.move", "retrieve_dashboard", [nextProps.domain], {
                context: this.props.context})
        });
    }
}

AccountDashBoard.template = "zet_account_accountant.accountDashboard";
