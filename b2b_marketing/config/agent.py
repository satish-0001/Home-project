from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label":_("Agent"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Call",
                    "label": _("Call"),
                    "description": _("Call"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Database"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Organization",
                    "label": _("Organization"),
                    "description": _("Organization"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Contact",
                    "label": _("Contact"),
                    "description": _("Contact"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Reports"),
            "items": [

                {
                    "type": "report",
                    "name": "Organization Contacts",
                    "doctype": "Campaigns",
                    "is_query_report": True,
                }
            ]
        }
    ]