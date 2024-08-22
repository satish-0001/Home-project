frappe.provide('frappe.dashboards.chart_sources');
frappe.dashboards.chart_sources["Quality"] = {
	method: "b2b_marketing.b2b_marketing.dashboard_chart_source.quality.quality.get",
    
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company")
		}
	]
}