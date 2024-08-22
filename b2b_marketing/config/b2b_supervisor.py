from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label":_("Campaigns"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Campaigns",
                    "label": _("Campaigns"),
                    "description": _("Campaigns"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label":_("Database"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Agents",
                    "label": _("Agents"),
                    "description": _("Agents"),
                    "link": "Tree/Agents",
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Campaign Lead",
                    "label": _("Leads"),
                    "description": _("Campaign Leads"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Report"),
            "items": [
                {
                    "type": "report",
                    "name": "Lead Report",
                    "doctype": "Campaigns Designer",
                    "is_query_report": True
                },
                {
                    "type": "report",
                    "name": "FTE Report",
                    "doctype": "Campaigns",
                    "is_query_report": True,
                },
                {
                    "type": "report",
                    "name": "Organization Contacts",
                    "doctype": "Campaigns",
                    "is_query_report": True,
                }
            ]
        }
    ]
