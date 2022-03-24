# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from odoo import api, exceptions, fields, models, _
from odoo.http import request
from odoo.exceptions import UserError, AccessError


class ActivityTags(models.Model):
	_name = "activity.tags"
	_description ="activity tags"

	name = fields.Char('Tags Name')
	color =fields.Integer("Colors")

class ResUsers(models.Model):
	_inherit = 'res.users'

	activity_manager = fields.Boolean('Activity Manager', help="Manager: Check all activities", implied_group='bi_all_in_one_schedule_activity.activity_manager')
	activity_supervisor = fields.Boolean('Activity Supervisor', help="Supervisor: Check only assigned activities", implied_group='bi_all_in_one_schedule_activity.activity_supervisor')

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	@api.model
	def _default_due_days(self):
		res = 1
		return res

	group_multi_user_activity = fields.Boolean("Multi Users", implied_group='bi_all_in_one_schedule_activity.group_multi_user_activity')
	group_multi_company_activity = fields.Boolean("Multi Company", implied_group='base.group_multi_company')

	due_activity_notification = fields.Boolean("Due Activity Notification")

	on_due_date = fields.Boolean("On Due Date")
	days_after_due_date = fields.Boolean("Days After Due Date")
	days_after_due_day = fields.Char("Days After Due Day", default=_default_due_days)
	days_before_due_date = fields.Boolean("Days Before Due Date")
	days_before_due_day = fields.Char("Days Before Due Day", default=_default_due_days)

	notify_create_user = fields.Boolean("Notify Create User")
	days_after_due_date_create = fields.Boolean("Days After Due Date Create Activity")
	days_after_due_day_create = fields.Char("Days After Due Day Create Activity", default=_default_due_days)
	days_before_due_date_create = fields.Boolean("Days Before Due Date Create Activity")
	days_before_due_day_create = fields.Char("Days Before Due Day Create Activity", default=_default_due_days)

	@api.onchange('group_multi_user_activity')
	def _onchange_group_multi_user_activity(self):
		if self.group_multi_user_activity:
			self.group_multi_user_activity = True

		if self.group_multi_user_activity == True:
			view = self.env['ir.ui.view'].sudo().search([('key', '=', 'bi_all_in_one_schedule_activity.user_id_disable_activity_inherit')])
			if view:
				view.active = False
		else:
			view = self.env['ir.ui.view'].sudo().search([('key', '=', 'bi_all_in_one_schedule_activity.user_id_disable_activity_inherit'),('active', '=', False)])
			if view:
				view.active = True

	@api.model
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		config_get_val = self.env['ir.config_parameter'].sudo()
		res.update(
			due_activity_notification = config_get_val.get_param('bi_all_in_one_schedule_activity.due_activity_notification'),
			on_due_date = config_get_val.get_param('bi_all_in_one_schedule_activity.on_due_date'),
			days_after_due_date=config_get_val.get_param('bi_all_in_one_schedule_activity.days_after_due_date'),
			days_after_due_day=config_get_val.get_param('bi_all_in_one_schedule_activity.days_after_due_day'),
			days_before_due_date=config_get_val.get_param('bi_all_in_one_schedule_activity.days_before_due_date'),
			days_before_due_day=config_get_val.get_param('bi_all_in_one_schedule_activity.days_before_due_day'),
			notify_create_user=config_get_val.get_param('bi_all_in_one_schedule_activity.notify_create_user'),
			days_after_due_date_create = config_get_val.get_param('bi_all_in_one_schedule_activity.days_after_due_date_create'),
			days_after_due_day_create = config_get_val.get_param('bi_all_in_one_schedule_activity.days_after_due_day_create'),
			days_before_due_date_create = config_get_val.get_param('bi_all_in_one_schedule_activity.days_before_due_date_create'),
			days_before_due_day_create = config_get_val.get_param('bi_all_in_one_schedule_activity.days_before_due_day_create'),
		)
		return res

	def set_values(self):
		super(ResConfigSettings, self).set_values()
		config_set_val = self.env['ir.config_parameter'].sudo()
		days_match = [1, 2, 3, 4, 5, 6]
		config_set_val.set_param('bi_all_in_one_schedule_activity.due_activity_notification', self.due_activity_notification)
		config_set_val.set_param('bi_all_in_one_schedule_activity.on_due_date', self.on_due_date)
		config_set_val.set_param('bi_all_in_one_schedule_activity.days_after_due_date', self.days_after_due_date)
		if self.days_after_due_day:
			config_set_val.set_param('bi_all_in_one_schedule_activity.days_after_due_day', 1 if int(self.days_after_due_day) not in days_match else self.days_after_due_day)
		else:	
			config_set_val.set_param('bi_all_in_one_schedule_activity.days_after_due_day', 1)
		config_set_val.set_param('bi_all_in_one_schedule_activity.days_before_due_date', self.days_before_due_date)
		if self.days_before_due_day:
			config_set_val.set_param('bi_all_in_one_schedule_activity.days_before_due_day', 1 if int(self.days_before_due_day) not in days_match else self.days_before_due_day)
		else:
			config_set_val.set_param('bi_all_in_one_schedule_activity.days_before_due_day', 1)	
		config_set_val.set_param('bi_all_in_one_schedule_activity.notify_create_user', self.notify_create_user)
		config_set_val.set_param('bi_all_in_one_schedule_activity.days_after_due_date_create', self.days_after_due_date_create)
		if self.days_after_due_day_create:
			config_set_val.set_param('bi_all_in_one_schedule_activity.days_after_due_day_create', 1 if int(self.days_after_due_day_create) not in days_match else self.days_after_due_day_create)
		else:
			config_set_val.set_param('bi_all_in_one_schedule_activity.days_after_due_day_create', 1)	
		config_set_val.set_param('bi_all_in_one_schedule_activity.days_before_due_date_create', self.days_before_due_date_create)
		if self.days_before_due_day_create:
			config_set_val.set_param('bi_all_in_one_schedule_activity.days_before_due_day_create', 1 if int(self.days_before_due_day_create) not in days_match else self.days_before_due_day_create)
		else:
			config_set_val.set_param('bi_all_in_one_schedule_activity.days_before_due_day_create', 1)	

class MailActivity(models.Model):
	_inherit = 'mail.activity'

	def redirect_origin(self):
		self.ensure_one()
		return {
			'name': 'Origin',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': self.res_model,
			'rec_name': 'Origin',
			'domain': [('id', '=', self.res_id)],
		}

	
	@api.model
	def _default_manager(self):
		res = request.env['res.users'].search([('activity_manager', '=', True)], limit=1)
		return res and res.id or False



	partner_id = fields.Many2one('res.partner', string='Partner')
	manager = fields.Many2one('res.users', string='Manager', default=_default_manager)
	summary = fields.Char('Summary', translate=True, required=True)
	supervisor = fields.Many2one('res.users', string='Supervisor')
	state = fields.Selection([
        ('overdue', 'Overdue'),
        ('today', 'Today'),
        ('planned', 'Planned'),
        ('done', 'Done'),('cancelled' , 'Cancelled')], 'State',
        compute='_compute_state' , readonly=True, copy=False,store=True)
	# state = fields.Selection(selection_add=[('done', 'Done') , ('cancelled' , 'Cancelled')])
	date_completion = fields.Date('Completed Date', index=True, readonly=True)
	active = fields.Boolean('Active', default=True)
	user_ids = fields.Many2many('res.users', string='Assigned to multi users', default=lambda self: self.env.user, required=True)
	company = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
	activity_tags_id = fields.Many2many('activity.tags' , string="Activity Tags")
	date_deadline = fields.Date('Due Date', index=True, required=True, default=fields.Date.context_today)
	res_model_id = fields.Many2one(
		'ir.model', 'Document Model',
		index=True, ondelete='cascade', required=True)
	res_model = fields.Char(
		'Related Document Model',
		index=True, related='res_model_id.model', compute_sudo=True, store=True, readonly=True)
	res_id = fields.Many2oneReference(string='Related Document ID', index=True, required=False, model_field='res_model')
	activity_feedback = fields.Char(string="Feedback")


	

	@api.model
	def action_activity_dashboard_redirect(self):
		return self.env.ref('bi_all_in_one_schedule_activity.activity_dashboard').read()[0]

	@api.onchange('user_id')
	def _onchange_user_id(self):
		self.user_ids = self.user_id

	@api.model
	def create(self, values):
		activity = super(MailActivity, self).create(values)
		user_ids = activity.user_ids
		remove_main_activity = False

		if len(user_ids) > 1:
			if request.env.user.has_group('bi_all_in_one_schedule_activity.group_multi_user_activity'):
				remove_main_activity = activity
				for usr_id in user_ids:
					activity = super(MailActivity, self).create(values)
					activity.user_id = usr_id
					activity.user_ids = usr_id

		else:
			activity.user_id = user_ids

		if remove_main_activity:
			remove_main_activity.unlink()
		return activity

	def write(self, values):
		user_ids_before = self.user_ids.ids
		user_id_before = self.user_id
		res = super(MailActivity, self).write(values)

		user_ids_after = self.user_ids.ids
		if res == True:
			if user_id_before != self.user_id:
				return res
			for usr_id in user_ids_after:
				if usr_id not in user_ids_before:
					raise exceptions.ValidationError(
						"You can not change the multi Assigned users in edit mode \n If you wish to change you can change Assigned to user")

		return res

	def _action_done(self, feedback=False, attachment_ids=None):
		""" Private implementation of marking activity as done: posting a message, deleting activity
			(since done), and eventually create the automatical next activity (depending on config).
			:param feedback: optional feedback from user when marking activity as done
			:param attachment_ids: list of ir.attachment ids to attach to the posted mail.message
			:returns (messages, activities) where
				- messages is a recordset of posted mail.message
				- activities is a recordset of mail.activity of forced automically created activities
		"""
		# marking as 'done'
		messages = self.env['mail.message']
		print("messages================ " , messages)
		next_activities_values = []
		print("next_activities_values---------------------------------------", next_activities_values)

		# Search for all attachments linked to the activities we are about to unlink. This way, we
		# can link them to the message posted and prevent their deletion.
		attachments = self.env['ir.attachment'].search_read([
			('res_model', '=', self._name),
			('res_id', 'in', self.ids),
		], ['id', 'res_id'])

		activity_attachments = defaultdict(list)
		for attachment in attachments:
			activity_id = attachment['res_id']
			activity_attachments[activity_id].append(attachment['id'])

		for activity in self:
			# extract value to generate next activities
			if activity.force_next:
				Activity = self.env['mail.activity'].with_context(
					activity_previous_deadline=activity.date_deadline)  # context key is required in the onchange to set deadline
				vals = Activity.default_get(Activity.fields_get())

				vals.update({
					'previous_activity_type_id': activity.activity_type_id.id,
					'res_id': activity.res_id,
					'res_model': activity.res_model,
					'res_model_id': self.env['ir.model']._get(activity.res_model).id,
				})
				virtual_activity = Activity.new(vals)
				virtual_activity._onchange_previous_activity_type_id()
				virtual_activity._onchange_activity_type_id()
				next_activities_values.append(virtual_activity._convert_to_write(virtual_activity._cache))
				print("next_activities_values---------------------------------------", next_activities_values)

			# post message on activity, before deleting it
			record = self.env[activity.res_model].browse(activity.res_id)
			print("record------------------------------" , record)
			record.message_post_with_view(
				'mail.message_activity_done',
				values={
					'activity': activity,
					'feedback': feedback,
					'display_assignee': activity.user_ids not in self.env.user
				},
				subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
				mail_activity_type_id=activity.activity_type_id.id,
				attachment_ids=[(4, attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
			)

			# Moving the attachments in the message
			# TODO: Fix void res_id on attachment when you create an activity with an image
			# directly, see route /web_editor/attachment/add
			activity_message = record.message_ids[0]
			message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
			if message_attachments:
				message_attachments.write({
					'res_id': activity_message.id,
					'res_model': activity_message._name,
				})
				activity_message.attachment_ids = message_attachments
			messages |= activity_message

		next_activities = self.env['mail.activity'].create(next_activities_values)

		self.sudo().write({'state':'done' , 'date_completion': date.today(), 'active': True})
		return messages, next_activities

	@api.depends('date_deadline')
	def _compute_state(self):
		for record in self.filtered(lambda activity: activity.date_deadline):
			tz = record.user_id.sudo().tz
			date_deadline = record.date_deadline
			if record.active == False:
				record.sudo().write({'state':'done'})
			else:
				record.state = self._compute_state_from_date(date_deadline, tz)

	

	def action_cancel(self):
		return self.write({'state': 'cancelled'})
		
	


	def _check_access_assignation(self):
		""" Check assigned user (user_id field) has access to the document. Purpose
		is to allow assigned user to handle their activities. For that purpose
		assigned user should be able to at least read the document. We therefore
		raise an UserError if the assigned user has no access to the document. """
		for activity in self:
			for user_id in activity.user_ids:
				model = self.env[activity.res_model].with_user(user_id).with_context(allowed_company_ids=user_id.company_ids.ids)
				try:
					model.check_access_rights('read')
				except exceptions.AccessError:
					raise exceptions.UserError(
						_('Assigned user %s has no access to the document and is not able to handle this activity.') %
						user_id.display_name)
				else:
					try:
						target_user = user_id
						target_record = self.env[activity.res_model].browse(activity.res_id)
						if hasattr(target_record, 'company_id') and (
								target_record.company_id != target_user.company_id and (
								len(target_user.sudo().company_ids) > 1)):
							return  # in that case we skip the check, assuming it would fail because of the company
						model.browse(activity.res_id).check_access_rule('read')
					except exceptions.AccessError:
						raise exceptions.UserError(
							_('Assigned user %s has no access to the document and is not able to handle this activity.') %
							user_id.display_name)

	def action_notify(self):
		if not self:
			return
		original_context = self.env.context
		body_template = self.env.ref('mail.message_activity_assigned')
		for activity in self:
			for user_id in activity.user_ids:
				if user_id.lang:
					# Send the notification in the assigned user's language
					self = self.with_context(lang=user_id.lang)
					body_template = body_template.with_context(lang=user_id.lang)
					activity = activity.with_context(lang=user_id.lang)
				model_description = self.env['ir.model']._get(activity.res_model).display_name
				body = body_template.render(
					dict(activity=activity, model_description=model_description),
					engine='ir.qweb',
					minimal_qcontext=True
				)
				record = self.env[activity.res_model].browse(activity.res_id)
				if user_id:
					record.message_notify(
						partner_ids=user_id.partner_id.ids,
						body=body,
						subject=_('%s: %s assigned to you') % (
						activity.res_name, activity.summary or activity.activity_type_id.name),
						record_name=activity.res_name,
						model_description=model_description,
						email_layout_xmlid='mail.mail_notification_light',
					)
				body_template = body_template.with_context(original_context)
				self = self.with_context(original_context)

	@api.model
	def _due_activity_notify_user(self):
		config_get_vals = self.env['ir.config_parameter'].sudo()
		due_activity_notification = config_get_vals.get_param('bi_all_in_one_schedule_activity.due_activity_notification')
		if due_activity_notification == 'True':
			on_due_date = config_get_vals.get_param('bi_all_in_one_schedule_activity.on_due_date')
			if on_due_date == 'True':
				days_after_due_date = config_get_vals.get_param('bi_all_in_one_schedule_activity.days_after_due_date')
				days_after_due_day = config_get_vals.get_param('bi_all_in_one_schedule_activity.days_after_due_day')
				days_before_due_date = config_get_vals.get_param('bi_all_in_one_schedule_activity.days_before_due_date')
				days_before_due_day = config_get_vals.get_param('bi_all_in_one_schedule_activity.days_before_due_day')
				today = date.today()
				template_id = self.env['ir.model.data'].get_object_reference('bi_all_in_one_schedule_activity','due_activity_notify_email_template')[1]
				email_template_obj = self.env['mail.template'].browse(template_id)
				if days_after_due_date == 'True':
					activities = self.env['mail.activity'].sudo().search([('active','=','True')])
					activities = activities.filtered(lambda activity: activity.date_deadline + timedelta(days=int(days_after_due_day)) == today)
					for activity in activities:
						values = email_template_obj.generate_email(activity.id, fields=['email_from','email_to','subject'])
						values['email_from'] = activity.create_uid.email
						values['email_to'] = activity.user_id.email
						values['body_html'] = '''
							<div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: rgb(255, 255, 255); ">
								<p>Dear ''' + activity.user_id.name + ''',</p>
								<br/>
								<p>Your Activity # ''' + activity.activity_type_id.name + ''', "''' + str(activity.summary) + '''" is due. </p>
								<p>Scheduled Date : ''' + str(activity.create_date.date()) + ''' </p>
								<p>Due date : ''' + str(activity.date_deadline) + ''' </p>
								<br/>
								<p>Thank you</p>
							</div>
						'''
						mail_mail_obj = self.env['mail.mail']
						msg_id = mail_mail_obj.create(values)
				if days_before_due_date == 'True':
					activities = self.env['mail.activity'].sudo().search([('active','=','True')])
					activities = activities.filtered(lambda activity: activity.date_deadline - timedelta(days=int(days_before_due_day)) == today)
					for activity in activities:
						values = email_template_obj.generate_email(activity.id, fields=['email_from','email_to','subject'])
						values['email_from'] = activity.create_uid.email
						values['email_to'] = activity.user_id.email
						values['body_html'] = '''
							<div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: rgb(255, 255, 255); ">
								<p>Dear ''' + activity.user_id.name + ''',</p>
								<br/>
								<p>Your Activity # ''' + activity.activity_type_id.name + ''', "''' + str(activity.summary) + '''" is due on ''' + str(activity.date_deadline) + '''
								<p>Scheduled Date : ''' + str(activity.create_date.date()) + ''' </p>
								<p>Due date : ''' + str(activity.date_deadline) + ''' </p>
								<br/>
								<p>Thank you</p>
							</div>
						'''
						mail_mail_obj = self.env['mail.mail']
						msg_id = mail_mail_obj.create(values)

			notify_create_user = config_get_vals.get_param('bi_all_in_one_schedule_activity.notify_create_user')
			if notify_create_user == 'True':
				days_after_due_date_create = config_get_vals.get_param('bi_all_in_one_schedule_activity.days_after_due_date_create')
				days_after_due_day_create = config_get_vals.get_param('bi_all_in_one_schedule_activity.days_after_due_day_create')
				days_before_due_date_create = config_get_vals.get_param('bi_all_in_one_schedule_activity.days_before_due_date_create')
				days_before_due_day_create = config_get_vals.get_param('bi_all_in_one_schedule_activity.days_before_due_day_create')
				today = date.today()
				template_id = self.env['ir.model.data'].get_object_reference('bi_all_in_one_schedule_activity','due_activity_notify_email_template')[1]
				email_template_obj = self.env['mail.template'].browse(template_id)
				if days_after_due_date_create == 'True':
					activities = self.env['mail.activity'].sudo().search([('active','=','True')])
					activities = activities.filtered(lambda activity: activity.date_deadline + timedelta(days=int(days_after_due_day_create)) == today)
					for activity in activities:
						values = email_template_obj.generate_email(activity.id, fields=['email_from','email_to','subject'])
						values['email_from'] = activity.create_uid.email
						values['email_to'] = activity.create_uid.email
						values['body_html'] = '''
							<div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: rgb(255, 255, 255); ">
								<p>Dear ''' + activity.create_uid.name + ''',</p>
								<br/>
								<p>You're created activity # ''' + activity.activity_type_id.name + ''', "''' + str(activity.summary) + '''" is due. </p>
								<p>Scheduled Date : ''' + str(activity.create_date.date()) + ''' </p>
								<p>Due date : ''' + str(activity.date_deadline) + ''' </p>
								<p>Assigned to  : ''' + activity.user_id.name + ''' </p>
								<br/>
								<p>Thank you</p>
							</div>
						'''
						mail_mail_obj = self.env['mail.mail']
						msg_id = mail_mail_obj.create(values)
				if days_before_due_date_create == 'True':
					activities = self.env['mail.activity'].sudo().search([('active','=','True')])
					activities = activities.filtered(lambda activity: activity.date_deadline - timedelta(days=int(days_before_due_day_create)) == today)
					for activity in activities:
						values = email_template_obj.generate_email(activity.id, fields=['email_from','email_to','subject'])
						values['email_from'] = activity.create_uid.email
						values['email_to'] = activity.create_uid.email
						values['body_html'] = '''
							<div style="font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: rgb(255, 255, 255); ">
								<p>Dear ''' + activity.create_uid.name + ''',</p>
								<br/>
								<p>You're created activity # ''' + activity.activity_type_id.name + ''', "''' + str(activity.summary) + '''" is due on ''' + str(activity.date_deadline) + '''
								<p>Scheduled Date : ''' + str(activity.create_date.date()) + ''' </p>
								<p>Due date : ''' + str(activity.date_deadline) + ''' </p>
								<p>Assigned to  : ''' + activity.user_id.name + ''' </p>
								<br/>
								<p>Thank you</p>
							</div>
						'''
						mail_mail_obj = self.env['mail.mail']
						msg_id = mail_mail_obj.create(values)