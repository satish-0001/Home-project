# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw

class EmployeeSize(Document):
	pass
	# def autoname(self):
	# 	self.name = self.employee_size

# def size_validation(employee_size, method):
# 	if employee_size.min_employee > employee_size.max_employee:
# 		frappe.throw(_("Please set Maximum Employee Size greater than the Minimum Employee Size"))