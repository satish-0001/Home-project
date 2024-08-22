from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils.dashboard import cache_source

@frappe.whitelist()
@cache_source
def get(chart_name = None, chart = None, no_cache = None, filters = None, from_date = None,
	to_date = None, timespan = None, time_interval = None, heatmap_year = None):
    labels, datapoints =[],[]
    doc = frappe.db.get_list('Industry Type',{"docstatus":0},["name"])
    for i in doc:
        labels.append(i.get("name"))
        adoc = frappe.db.sql("""select count(name) from `tabCampaign Organization` where industry = "{0}" """.format(i.get("name")),as_dict=True)
        for a in adoc:
            datapoints.append(a.get("count(name)"))
    return{
    "labels":labels,
    "datasets": [{
        "name": _("Industry Type"),
        "values": datapoints
    }],
    "type": "donut"
    }