/** @odoo-module */

import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";
import { patch } from "@web/core/utils/patch";
import { useState, onWillUpdateProps } from "@odoo/owl";

patch(AnalyticDistribution.prototype, {
    setup(){
        super.setup();
         this.state = useState({
           ...this.state,
            selectPlans: []
        });
        onWillUpdateProps(nextProps => {
            this.props.readonly = false
          });
    },

    onChangeInpSelectPlan(ev){
        const namePlan = ev.target.value
        this.allPlans.forEach((plan)=>{
            if (plan.name === namePlan){
                this.state.selectPlans.push(plan)
            }
        })
        ev.target.value = null
    },

    get selectPlans(){
        const plans = []
        this.state.formattedData.forEach((item)=>{
            item.analyticAccounts.forEach((plan)=>{
                if (plan.accountDisplayName){
                    this
                    plans.push({
                        id:plan.planId,
                        color:plan.accountColor,
                        name:plan.planName
                    })
                }
            })

        })
        plans.push(...this.state.selectPlans)

        return Array.from(new Map(plans.map(plan => [plan.id, plan])).values());
    },

    get selectPlanInput(){
        return this.allPlans.filter(itemA =>
            !this.selectPlans.some(itemB => itemB.id === itemA.id)
        )
    },

    deleteSelectPlan(plan){
        this.state.selectPlans = this.state.selectPlans.filter(item => item !== plan)
    },
});
