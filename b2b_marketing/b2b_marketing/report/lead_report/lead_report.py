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
			"label": _("Lead"),
			"options": "Campaign Lead",
			"fieldname": "lead",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Customer Name"),
			"options": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
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
			"label": _("Call"),
			"options": "Call",
			"fieldname": "call",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("First Name"),
			"fieldname": "first_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Last Name"),
			"fieldname": "last_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Title"),
			"fieldname": "title",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Seniority"),
			"options":"Seniority",
			"fieldname": "seniority",
			"fieldtype": "Link",
			"width": 120
		},
	
		{
			"label": _("Email ID"),
			"fieldname": "email",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Organization Code"),
			"options": "Campaign Organization",
			"fieldname": "organization",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Organization Name"),
			"fieldname": "organization_name",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Organization Number"),
			"fieldname": "organization_num",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Address"),
			"fieldname": "address",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("City"),
			"fieldname": "city",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("State"),
			"fieldname": "state",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Postal Code"),
			"fieldname": "postal_code",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Country"),
			"options":"Country",
			"fieldname": "country",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("#Employees"),
			"fieldname": "employees",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Sub Industry"),
			"options":"Sub Industry Type",
			"fieldname": "sub_industry",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Main Industry"),
			"options":"Industry Type",
			"fieldname": "main_industry",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Website Link"),
			"fieldname": "website",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Revenue Size"),
			"fieldname": "revenue_size",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Organization Link"),
			"fieldname": "organization_Link",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Domain"),
			"fieldname": "domain",
			"fieldtype": "Data",
			"width": 120
		}
		]
	return columns


def get_data(filters):
	conditions = get_conditions(filters)
	data = []
	query = """select
				first_name,
				last_name,
				title,
				seniority,
				email,
				organization_num,
				organization,
				organization_name,
				address,
				city,
				state,
				country,
				postal_code,
				employees,
				revenue_size,
				main_industry,
				sub_industry,
				website,
				salutation,
				lead,
				call_id,
				customer,
				campaign
				from `tabLead Report`"""

	if conditions:
		query = query+conditions
	result =frappe.db.sql(query,as_dict=True)
	for res in result:
		row ={
			"lead": res.get("lead"),
			"customer": res.get("customer"),
			"campaign": res.get("campaign"),
			"call": res.get("call_id"),
			"first_name":res.get("first_name"),
			"last_name":res.get("last_name"),
			"title":res.get("title"),
			"seniority":res.get("seniority"),
			"email":res.get("email"),
			"organization":res.get("organization"),
			"organization_name":res.get("organization_name"),
			"organization_num":res.get("organization_num"),
			"address":res.get("address"),
			"city":res.get("city"),
			"state":res.get("state"),
			"postal_code":res.get("postal_code"),
			"country":res.get("country"),
			"employee_size":res.get("employee_size"),
			"sub_industry":res.get("sub_industry"),
			"main_industry":res.get("main_industry"),
			"website":res.get("website"),
			"revenue_size":res.get("revenue_size"),
			"organization_Link":res.get("organization_link"),
			"domain":res.get("domain")

		}
		data.append(row)
	return data


def get_conditions(filters):
	if filters:
		condition = "where "
		if filters.get("title"):
			condition +="title LIKE '%{0}%' and ".format(filters.get("title"))
		if filters.get("seniority"):
			condition +="seniority = '{0}' and ".format(filters.get("seniority"))
		# if filters.get("level"):
		# 	condition +="level ='{0}' and ".format(filters.get("level"))
		if filters.get("organization"):
			condition +="organization ='{0}' and ".format(filters.get("organization"))
		if filters.get("country"):
			condition +="country ='{0}' and ".format(filters.get("country"))
		if filters.get("sub_industry"):
			condition += "sub_industry ='{0}' and ".format(filters.get("sub_industry"))
		if filters.get("main_industry"):
			condition += "main_industry ='{0}' and ".format(filters.get("main_industry"))
		if filters.get("customer"):
			condition +="customer ='{0}' and ".format(filters.get("customer"))
		if filters.get("campaign"):
			condition +="campaign ='{0}' and ".format(filters.get("campaign"))
		return condition[:-4]
	return False

