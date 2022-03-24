# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class ScheduleActivityBackend(http.Controller):

    @http.route('/activity/fetch_dashboard_data', type="json", auth='user')
    def activity_fetch_dashboard_data(self):
        activity_data = request.env['mail.activity'].sudo().search([])
        dashboard_data = {
            'activities': activity_data,
            'activity_count': len(activity_data),
        }
        dashboard_data['activity_models'] = activity_data.mapped('res_model_id').read(['id', 'name', 'model'])

        return dashboard_data