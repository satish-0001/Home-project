from erpnext.setup.doctype.terms_and_conditions.terms_and_conditions import TermsandConditions

import frappe
from frappe import _, throw
from frappe.model.document import Document
from frappe.utils import cint
from frappe.utils.jinja import validate_template


class CustomTermsandConditions(TermsandConditions):
	def validate(self):
		if self.terms:
			validate_template(self.terms)
		if (
			not cint(self.buying)
			and not cint(self.selling)
			and not cint(self.hr)
			and not cint(self.disabled)
			and not cint(self.is_call_script)
		):
			throw(_("At least one of the Applicable Modules should be selected"))









