/** @odoo-module **/

import ActivityMenu from '@mail/js/systray/systray_activity_menu';
const { Component } = owl;

ActivityMenu.include({
     start: function () {
        this._super.apply(this, arguments)
        Component.env.bus.on('systray_get_activities', this, this._updateActivityPreview);
     },
     _getActivityData: function () {
        var self = this;

        return self._rpc({
            model: 'res.users',
            method: 'systray_get_activities',
            args: [],
        }).then(function (data) {
            self._activities = data;
            self.activityCounter = _.reduce(data, function (total_count, p_data) { return total_count + p_data.total_count || 0; }, 0);
            self.$('.o_notification_counter').text(self.activityCounter);
            if (self.activityCounter > 99) {
                self.$('.o_notification_counter').addClass('o_counter-100');
            };
            self.$el.toggleClass('o_no_notification', !self.activityCounter);
        });
    },
})
