// Copyright (c) 2024, Dexciss and contributors
// For license information, please see license.txt

frappe.query_reports["Call Analytics"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.str_to_obj(frappe.datetime.add_months(frappe.datetime.get_today(), -1)),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "campaign",
            "label": __("Campaign"),
            "fieldtype": "MultiSelectList",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Campaigns", txt);
            }
        },
        {
            "fieldname": "supervisor",
            "label": __("Supervisor"),
            "fieldtype": "MultiSelectList",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Agents", txt, {
                    "is_group": 1
                });
            }
        },
        {
            "fieldname": "agent",
            "label": __("Agent"),
            "fieldtype": "MultiSelectList",
            "get_data": function(txt) {
                return frappe.db.get_link_options("Agents", txt);
            }
        },
		{
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "based_on",
            "label": __("Based On"),
            "fieldtype": "Select",
            "options": ["Agent", "Campaign", "Supervisor", "Customer"],
            "default": "Agent"
        }
    ]
};
