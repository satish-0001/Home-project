from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils.dashboard import cache_source

@frappe.whitelist()
@cache_source
def get(chart_name = None, chart = None, no_cache = None, filters = None, from_date = None,
	to_date = None, timespan = None, time_interval = None, heatmap_year = None):

    labels,  datapoints = [], []
    lst = [{"status":"To Start"},{"status":"Running"},{"status":"Cancelled"},{"status":"Completed"},{"status":"Past Due"}]
    for x in lst:
        doc = frappe.db.sql(""" select count(name) from `tabCampaigns` where status ='{0}' """.format(x.get("status")),as_dict=1)
        labels.append(x.get("status"))
        for i in doc:
            datapoints.append(i.get("count(name)"))
    return{
    "labels":labels,
    "datasets": [{
        "name": _("campaigns"),
        "values": datapoints
    }],
    "type": "bar"
    }