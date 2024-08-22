// Copyright (c) 2016, Dexciss and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Organization Contacts"] = {
        "filters": [
            {
			"fieldname":"organization",
			"label": __("Organization Name"),
			"fieldtype": "Link",
			"options":"Campaign Organization"
		}
	]
};
