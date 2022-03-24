# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'All in one Schedule Activity Management -Advance Feature',
    'category': 'Extra Tools',
    'version': '13.0.0.2',
    'summary': 'Advance Schedule Activity multi users assign schedule activity to multi users Schedule Activity Dashboard for schedule activity history of schedule activity reports for schedule activity menu and view for schedule activities for Multi Company Activity',
    'description': """

        All in one Schedule Activity Management in odoo,
        Manage Multi user in activity in odoo,
        Manage activity supervisor in odoo,
        Manage activity manager in odoo,
        Different activities in odoo,
        Activities filter by in odoo,
        Activity Management Dashboard in odoo, 


    """,
    'author': 'BrowseInfo',
    'price': 35,
    'currency': "EUR",
    'website': 'https://www.browseinfo.in',
    'depends': ['mail'],
    
    'data': [
        'security/activity_security.xml',
        'security/ir.model.access.csv',
        'data/due_activity_notify_email_template.xml',
        'data/due_activity_notify_cron.xml',
        'views/assets.xml',
        'views/mail_activity_views.xml',
    ],
    'qweb': ["static/src/xml/activity_dashboard.xml"],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/x1n0QIFRes8',
    'images':["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
