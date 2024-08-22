# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class SubIndustryType(Document):
	def autoname(self):
		if self.main_industry:
			self.name = str(self.sub_industry) + " [" + str(self.main_industry) + "]"
		else:
			self.name = str(self.sub_industry)
