# Copyright (c) 2013, Dexciss and contributors
# For license information, please see license.txt

# import frappe

# Copyright (c) 2013, Dexciss Technology and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns=get_columns(filters)
	data = get_data(filters)
	return columns,data


def get_columns(filters):
	columns=[
			{
				"label": _("Name"),
				"fieldname": "name",
				"fieldtype": "Link",
				"options": "Campaigns",
				"width": 140
			},
			{
				"label": _("Campaign Name"),
				"fieldname": 'campaigns_name',
				"fieldtype": "Read Only",
				"width": 100
			},
			{
				"label": _("Status"),
				"fieldname": 'status',
				"fieldtype": "Data",
				"width": 100
			},

			{
				"label": _("Started On"),
				"fieldname": 'start_on',
				"fieldtype": "Datetime",
				"width": 100
			},
			{
				"label": _("Supervisor"),
				"fieldname": 'agent_name',
				"fieldtype": "Link",
				"options":"Agents",
				"width": 100
			},
			{
				"label": _("Company"),
				"fieldname": 'company',
				"fieldtype": "Link",
				"options" : "Company",
				"width": 100
			},
			{
				"label": _("Total Available Contacts"),
				"fieldname": 'total_available_contacts',
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _("Delivery Target"),
				"fieldname": 'delivery_target',
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _("Daily Cap"),
				"fieldname": 'daily_cap',
				"fieldtype": "Data",
				"width": 100
			},
			{
				"label": _("Lead Per Organization"),
				"fieldname": 'lead_company_count',
				"fieldtype": "data",
				"width": 100
			},
			{
				"label": _(" Campaign Lead"),
				"fieldname": 'campaign_lead',
				"fieldtype": "link",
				"option" : "Campaign Lead",
				"width": 100
			},
			{
				"label": _(" Call"),
				"fieldname": 'call',
				"fieldtype": "link",
				"option" : "Call",
				"width": 100
			},
			{
				"label": _(" Campaign Success ratio"),
				"fieldname": 'campaign_success _ratio',
				"fieldtype": "float",
				"width": 100
			},
			{
				"label": _(" Call success ration"),
				"fieldname": 'call_success _ratio',
				"fieldtype": "float",
				"width": 100
			},
			{
				"label": _(" Avg Daily Lead"),
				"fieldname": 'avg_daily_lead',
				"fieldtype": "float",
				"width": 100
			},
			{
				"label": _(" Avg Daily Calls"),
				"fieldname": 'avg_daily_calls',
				"fieldtype": "float",
				"width": 100
			},
			
	]
	return columns


def get_condition(filters):

	conditions=" "
	if filters.get("customer_name"):
			conditions += "AND c.customer_name= '%s'" % filters.get('customer_name')
	if filters.get("campaigns"):
			conditions += "AND c.name = '%s'" % filters.get('campaigns')
	if filters.get("agent_name"):
			conditions += "AND c.agent_name = '%s'" % filters.get('agent_name')
	if filters.get("company"):
			conditions += "AND c.company = '%s'" % filters.get('company')
	if filters.get("start_on"):
			conditions += "AND c.start_on >= '%s'" % filters.get('start_on')
	if filters.get("end_on"):
			conditions += "AND c.start_on <= '%s'" % filters.get('end_on')
	return conditions
		


def get_data(filters):
	conditions=get_condition(filters)
	doc=frappe.db.sql("""select c.name,c.campaigns_name,c.status,c.start_on,c.agent_name,c.company,
		c.total_available_contacts,c.delivery_target,c.daily_cap,c.lead_company_count,
		 case when c.delivery_target != 0 then
		 (c.lead_company_count/c.delivery_target) 
		 when c.delivery_target = 0 then 
		 'NA '
		 end as 'campaign_success _ratio',
		
	
		(select count(cl.name) FROM `tabCampaign Lead` cl where c.name = cl.campaign )  as 'campaign_lead',

		(select count(name) FROM `tabCall` cc where c.name = cc.campaign ) as 'call',
	
		(select count(cl.name) FROM `tabCampaign Lead` cl where c.name = cl.campaign ) /(select count(name) FROM `tabCall` cc where c.name = cc.campaign ) 
		as 'call_success _ratio',
		
		(select count(cl.name) FROM `tabCampaign Lead` cl where c.name = cl.campaign )/
		(select datediff(end_on,start_on)   FROM `tabCampaigns Designer`  cd where c.campaigns_name = cd.name)
		 as 'avg_daily_lead',


		(select count(name) FROM `tabCall` cc where c.name = cc.campaign ) /
		(select datediff(end_on,start_on)   FROM `tabCampaigns Designer`  cd where c.campaigns_name = cd.name)
		 as 'avg_daily_calls'





		
							From `tabCampaigns` c
		 					Where c.docstatus = 0
		 				{conditions}""".format(conditions=conditions),filters,as_dict = True)
	return doc

		


















