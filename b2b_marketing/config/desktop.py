# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "B2B Marketing",
			"color": "grey",
			"icon": "octicon octicon-radio-tower",
			"type": "module",
			"label": _("Marketing")
		},
		{
			"module_name": "B2B Supervisor",
			"color": "grey",
			"icon": "octicon octicon-megaphone",
			"type": "module",
			"label": _("Supervisor")
		},
		{
			"module_name": "Agent",
			"color": "grey",
			"icon": "octicon octicon-person",
			"type": "module",
			"label": _("Agent")
		}
	]
