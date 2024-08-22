// Copyright (c) 2016, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Pending Quality Review"] = {
	"filters": [
	    {
			"fieldname": "quality_type",
			"label": __("Quality Type"),
			"fieldtype": "Select",
			"options": '\nOrganization\nContact\nCampaign Lead\nCall\nAddress'
		},
        {
            "fieldname": "campaign",
			"label": __("Campaign"),
			"options": "Campaigns",
			"fieldtype": "Link",
			"width": 200
		},
        {
            "fieldname": "agent",
			"label": __("Agent"),
			"options": "Agents",
			"fieldtype": "Link",
			"width": 200
		},
	]
};
