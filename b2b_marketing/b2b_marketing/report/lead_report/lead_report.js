// Copyright (c) 2016, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Lead Report"] = {
	"filters": [
		{
		    fieldname: "title",
			label: __("Title"),
			fieldtype: "Data",
		},
		{
			label: __("Seniority"),
			options:"Seniority",
			fieldname: "seniority",
			fieldtype: "Link"
		},
		
		{
			fieldname:"organization",
			label: __("Organization"),
			fieldtype: "Link",
			options: "Campaign Organization"
		},
		{
			fieldname:"country",
			label: __("Country"),
			fieldtype: "Link",
			options: "Country"
		},
		{
			label: __("Sub Industry"),
			options:"Sub Industry Type",
			fieldname: "sub_industry",
			fieldtype: "Link"
		},
		{
			label: __("Main Industry"),
			options:"Industry Type",
			fieldname: "main_industry",
			fieldtype: "Link"
		},
		{
			label: __("Customer Name"),
			options:"Customer",
			fieldname: "customer",
			fieldtype: "Link"
		},
		{
			label: __("Campaign"),
			options:"Campaigns",
			fieldname: "campaign",
			fieldtype: "Link"
		},
	]
};
