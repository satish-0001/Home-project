from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils.dashboard import cache_source

@frappe.whitelist()
@cache_source
def get(chart_name = None, chart = None, no_cache = None, filters = None, from_date = None,
	to_date = None, timespan = None, time_interval = None, heatmap_year = None):
    labels, datapoints =[],[]
    lst = [{ "status":"Open"},{"status":"Closed"},{"status":"Cancelled"},{"status":"Amended"}]
    for x in lst:
        doc = frappe.db.sql("""select count(name) from `tabQuality Review` where status = '{0} '""".format(x.get("status")),as_dict=True)
        labels.append(x.get("status"))
        for a in doc:
            datapoints.append(a.get("count(name)"))
    return{
    "labels":labels,
    "datasets": [{
        "name": _("unit"),
        "values": datapoints
    }],
    "type": "bar"
    }