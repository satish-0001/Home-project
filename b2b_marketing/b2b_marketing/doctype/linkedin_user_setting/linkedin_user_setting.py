# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from linkedin_api import Linkedin

class LinkedInUserSetting(Document):
	def validate(self):
		self.check_validation()

	@frappe.whitelist()
	def check_validation(self):
		try:
			# Authenticate using any Linkedin account credentials
			if self.user_name and self.password:
				password =self.get_password(fieldname="password", raise_exception=False)
				api = Linkedin(self.user_name, password)
		except:
			frappe.throw(_("Invalid LinkedIn User name and Password"))