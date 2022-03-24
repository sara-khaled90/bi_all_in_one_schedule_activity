odoo.define('bi_all_in_one_schedule_activity_backend.activity_dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var ActivityDashboard = AbstractAction.extend({
    hasControlPanel: true,
    contentTemplate: 'bi_all_in_one_schedule_activity.ActivityDashboardMain',

    events: {
        'click .filterActivities': 'clickActivities',
        'click .filterByModel': 'clickActivityByModel',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.date_range = 'week';
        this.date_from = moment().subtract(1, 'week');
        this.date_to = moment();
        this.dashboards_templates = ['bi_all_in_one_schedule_activity.dashboard_header', 'bi_all_in_one_schedule_activity.dashboard_content'];
    },

    willStart: function() {
        var self = this;
        return self.fetch_data();
    },

    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            //self.render_dashboards();
            self.$el.parent().addClass('oe_background_grey');
        });
    },

    fetch_data: function() {
        var self = this;
        var def1 = this._rpc({
            route: '/activity/fetch_dashboard_data',
        })
        def1.then(function (result) {
            self.data = result;
            self.activity_models = result.activity_models;
            self.activities = result.activities;
            self.activity_count = result.activity_count;
        });
        return def1
    },

    render_dashboards: function() {
        var self = this;
        _.each(this.dashboards_templates, function(template) {
            self.$('.o_activity_dashboard').append(QWeb.render(template, {widget: self}));
        });
    },

    on_reverse_breadcrumb: function() {
        var self = this;
        web_client.do_push_state({});
        this.update_cp();
        this.fetch_data().then(function() {
            self.$('.o_activity_dashboard').empty();
            self.render_dashboards();
        });
    },

    update_cp: function() {
        var self = this;
    },

    clickActivities: function (ev) {
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var activity_type_name = $action.data('activity_type');
        this.do_action({
            name: activity_type_name,
            res_model: 'mail.activity',
            res_id: false,
            views: [[false, 'list'],[false, 'form'],[false, 'calendar'],[false, 'kanban'],[false, 'pivot'],[false, 'graph']],
            type: 'ir.actions.act_window',
            domain: $action.data('domain'),
        }, {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb
        });
    },

    clickActivityByModel: function (ev) {
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var activity_name = $(ev.currentTarget).find("span").html();
        var model_name = $action.parents(".activity_model_block").find(".res_model").val();
        var domain_filter = $action.data('domain_filter');
        var activity_type = $action.data('activity_type');
        var activity_date = $action.data('date');
        var activity_type_name = $action.data('activity_type_name');
        var currentDate = new Date(new Date().getTime() + 24 * 60 * 60 * 1000);
        var day = currentDate.getDate()
        var month = currentDate.getMonth() + 1
        var year = currentDate.getFullYear()
        var date_output = month + "/" + day + "/" + year
        var date=new Date();
        var today_date=(date.getMonth()+1)+"/"+date.getDate()+"/"+date.getFullYear();

        if(domain_filter == 'today'){
            var $dom = "[('res_model','=','"+model_name+"'),('date_deadline','=','"+today_date+"')]"
        }
        else if(domain_filter == 'overdue'){
            var $dom = "[('res_model','=','"+model_name+"'),('date_deadline','<','"+today_date+"')]"
        }
        else if(domain_filter == 'planned'){
            var $dom = "[('res_model','=','"+model_name+"'),('date_deadline','>','"+today_date+"')]"
        }
        else if(activity_type){
            var $dom = "[('res_model','=','"+model_name+"'),('activity_type_id','ilike','"+activity_type+"'),('date_deadline','=','"+today_date+"')]"
        }
        else if(activity_date){
            var $dom = "[('res_model','=','"+model_name+"'),('date_deadline','=', '"+date_output+"')]"
        }
        else{
            var $dom = "[('res_model','=','"+model_name+"')]"
        }
        this.do_action({
            name: activity_type_name,
            res_model: 'mail.activity',
            res_id: false,
            views: [[false, 'list'],[false, 'form'],[false, 'calendar'],[false, 'kanban'],[false, 'pivot'],[false, 'graph']],
            type: 'ir.actions.act_window',
            domain: $dom,
        }, {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb
        });
    },
});

core.action_registry.add('activity_dashboard', ActivityDashboard);
return ActivityDashboard;
});
