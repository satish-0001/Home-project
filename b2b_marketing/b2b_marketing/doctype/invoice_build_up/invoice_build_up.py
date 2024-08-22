# -*- coding: utf-8 -*-
# Copyright (c) 2020, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class InvoiceBuildUp(Document):
	pass

@frappe.whitelist()
def make_campaign_invoice(source_name, target_doc=None, ignore_permissions=False):
	def set_item_in_sales_invoice(source, target):
		sale_inv = frappe.get_doc(target)
		item_id = frappe.get_doc("Item",source.item)
		account = frappe.db.sql("""select income_account FROM `tabItem Default` where parent =%s and parenttype='Item' limit 1""",(source.item))
		sale_inv.append("items",{"item_code":source.item,
								 "item_name":item_id.item_name,
								 "qty":1,
								 "uom":"Nos",
								 "conversion_factor":1,
								 "rate":source.charge,
								 "income_account":account[0][0],
								 "cost_center":source.cost_center,
								 "description":item_id.description,
								 "invoice_build_up":source.name,
								 "campaigns_name":source.campaigns_name
								 })

	doclist = get_mapped_doc("Invoice Build Up", source_name, {
		"Invoice Build Up": {
			"doctype": "Sales Invoice",
		}
	}, target_doc,set_item_in_sales_invoice)
	return doclist

def change_invoice_build_up_status(invoice,mehtod):
	inv =frappe.db.sql("""select invoice_build_up from `tabSales Invoice Item` where  parent =%s and parenttype='Sales Invoice' and invoice_build_up is not null""",(invoice.name),as_dict=True)
	for s in inv:
		build = frappe.get_doc("Invoice Build Up",s.get('invoice_build_up'))
		build.invoice = invoice.name
		build.status ="Billed"
		build.save(ignore_permissions=True)