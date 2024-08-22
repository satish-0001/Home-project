frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Campaigns"] = {
	method: "b2b_marketing.b2b_marketing.dashboard_chart_source.campaigns.campaigns.get",
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