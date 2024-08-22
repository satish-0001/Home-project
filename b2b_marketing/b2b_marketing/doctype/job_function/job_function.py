# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class JobFunction(Document):
	def autoname(self):
		if self.department:
			self.name = str(self.job_function_name) + " [" + str(self.department) + "]"
		else:
			self.name = str(self.job_function_name)