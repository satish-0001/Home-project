# Copyright (c) 2013, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": _("Quality Review"),
			"options": "Quality Review",
			"fieldname": "quality_review",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Goal"),
			"options": "Quality Goal",
			"fieldname": "quality_goal",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Quality Type"),
			"options": "DocType",
			"fieldname": "quality_type",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Value"),
			"fieldname": "value",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Campaign"),
			"options": "Campaigns",
			"fieldname": "campaign",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Agent"),
			"options": "Agents",
			"fieldname": "agent",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120
		}
	]
	return columns

def get_data(filters):
	query = """select name,goal,date,quality_type,value,campaign,agent,status from `tabQuality Review` where status ='Open' """
	data = []
	condition = get_condition(filters)
	if condition:
		query += condition
	result = frappe.db.sql(query,as_dict=True)
	for res in result:
		row ={
			"quality_review":res.get("name"),
			"quality_goal":res.get("goal"),
			"date":res.get("date"),
			"quality_type":res.get("quality_type"),
			"value":res.get("value"),
			"campaign":res.get("campaign"),
			"agent":res.get("agent"),
			"status":res.get("status")
		}
		data.append(row)
	return data


def get_condition(filters):
	if filters:
		condition ="and "
		if filters.get("quality_type"):
			condition += "quality_type ='{0}' and ".format(filters.get("quality_type"))
		if filters.get("campaign"):
			condition += "campaign ='{0}' and ".format(filters.get("campaign"))
		if filters.get("agent"):
			condition += "agent ='{0}' and ".format(filters.get("agent"))
		return condition[:-4]
	return False
