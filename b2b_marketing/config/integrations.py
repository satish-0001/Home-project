from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Viva Communication Settings"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Viva Communication",
					"description": _("Viva Communication settings"),
				},

			]
		}
	]
