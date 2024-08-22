// Copyright (c) 2016, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["FTE Report"] = {
	"filters": [
		{
			label: __("Campaign Name"),
			options:"Campaigns",
			fieldname: "campaign",
			fieldtype: "Link"
		},
		{
			label: __("Customer ID"),
			options:"Customer",
			fieldname: "customer_name",
			fieldtype: "Link"
		},
	]
};
