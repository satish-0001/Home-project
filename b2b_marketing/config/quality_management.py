from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Reports"),
			"items": [
				{
					"type": "report",
					"name": "Pending Quality Review",
					"doctype": "Quality Review",
					"is_query_report": True,
					"onboard": 1,
				},
				{
					"type": "report",
					"name": "QC Report",
					"doctype": "Quality Review",
					"is_query_report": True,
				},
			]
		},
		{
			"label": _("Goal and Procedure"),
			"items": [
				{
					"type": "doctype",
					"name": "Quality Points",
					"label": _("Quality Points"),
					"description": _("Quality Points")

				}
			]

		}
	]