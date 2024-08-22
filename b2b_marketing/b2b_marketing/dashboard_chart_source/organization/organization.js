frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Organization"] = {
	method: "b2b_marketing.b2b_marketing.dashboard_chart_source.organization.organization.get",
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		}
	]
};