# Copyright (c) 2013, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns =get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": _("Method"),
			"fieldname": "method",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Delivery Status"),
			"fieldname": "delivery_status",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Owner"),
			"fieldname": "owner",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Customer ID"),
			"fieldname": "customer_id",
			"options": "Customer",
			"fieldtype": "link",
			"width": 120
		},
		{
			"label": _("Customer Name"),
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Campaign Name"),
			"options": "Campaigns",
			"fieldname": "campaign",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Total Working Days"),
			"fieldname": "total_working_days",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Hours"),
			"fieldname": "hours",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Total HD"),
			"fieldname": "total_hd",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Total Hour's"),
			"fieldname": "total_hours",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Agent Wise Campaign Hour's"),
			"fieldname": "agent_wise_campaign_hour",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Agent Wise campaign FTE Report"),
			"fieldname": "agent_wise_campaign_fte_report",
			"fieldtype": "Data",
			"width": 120
		},
	]
	return columns

def get_data(filters):
	data = []
	query = """select TC.name,
				TCD.campaing_type,
				TC.completed_by as owner,
				TC.campaign,
				TCD.customer_name,
				TCD.customer,
				TCD.start_on,
				TCD.end_on,
				TCD.days,
				TST.start_time,
				TST.end_time,
				tcmg.status
				from `tabCall` as TC
				inner join `tabCampaigns` as tcmg  on TC.campaign = tcmg.name
				inner join `tabCampaigns Designer`as TCD on TCD.name = tcmg.campaigns_name
				inner join `tabUser` TU on TU.name = TC.completed_by
				left join `tabEmployee` TE on TE.user_id = TU.name
				left join `tabShift Type` TST on TST.name = TE.default_shift"""

	conditions = get_condition(filters)
	if conditions:
		query += conditions
	result_set = frappe.db.sql(query,as_dict=True)
	print("jdbhcbhjbfvhjbfvhjfvbhjfvbhjf",result_set)

	for res in result_set:
		row ={
			"method":res.get("campaing_type"),
			"delivery_status":res.get("status"),
			"owner":res.get("owner"),
			"customer_id":res.get("customer_name"),
			"customer_name":res.get("customer"),
			"campaign":res.get("campaign"),
			"start_date":res.get("start_on"),
			"end_date":res.get("end_on"),
			"total_working_days":res.get("days"),
			"hours":res.get(""),
			"total_hd":res.get(""),
			"total_hours":res.get(""),
			"agent_wise_campaign_hour":res.get(""),
			"agent_wise_campaign_fte_report":res.get(""),
		}
		if res.get("start_time") and res.get("end_time"):
			hours = (res.get("end_time") - res.get("start_time"))
			row["hours"] = int(res.get("days")) * int(str(hours).split(":")[0])
			row["agent_wise_campaign_hour"] = str(hours).split(":")[0]

		data.append(row)
	return data

def get_condition(filters):
	if filters:
		condition = " where "
		if filters.get("campaign"):
			condition +="TC.campaign ='{0}' and ".format(filters.get("campaign"))
		if filters.get("customer_name"):
			condition +="TCD.customer_name ='{0}' and ".format(filters.get("customer_name"))
		return condition[:-4]
	return False