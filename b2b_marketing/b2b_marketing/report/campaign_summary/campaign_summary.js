// Copyright (c) 2016, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Campaign Summary"] = {
	"filters": [
		{
			fieldname: "customer_name",
			label: __("Customer"),
			fieldtype: "Link",
			options:"Customer",
			default: "",
			reqd: 0
		},
		{
			fieldname: "campaigns",
			label: __("Campaigns"),
			fieldtype: "Link",
			options:"Campaigns",
			default: "",
			reqd: 0
		},
		{
			fieldname: "agent_name",
			label: __("Supervisor"),
			fieldtype: "Link",
			options:"Agents",
			default: "",
			reqd: 0
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options:"Company",
			default: "",
			reqd: 0
		},
		{
			fieldname: "start_on",
			label: __("Start On"),
			fieldtype: "Date",
			options:"Campaigns Designer",
			default: "",
			reqd: 0
		},
		{
			fieldname: "end_on",
			label: __("End On"),
			fieldtype: "Date",
			options:"Campaigns Designer",
			default: "",
			reqd: 0
		},

	]
};
