# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw

class RevenueSize(Document):
	pass
	# def autoname(self):
	# 	self.name = self.revenue_size

# def size_validation(revenue_size, method):
# 	if revenue_size.min_revenue > revenue_size.max_revenue:
# 		frappe.throw(_("Please set Maximum Revenue greater than the Minimum Revenue"))
