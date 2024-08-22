from __future__ import unicode_literals
from frappe import _

def get_data():
    return [
        {
            "label":_("Campaigns"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Campaigns Designer",
                    "label": _("Campaigns Designer"),
                    "description": _("Campaigns Designer"),
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
                {
                    "type": "doctype",
                    "name": "Address",
                    "label": _("Address"),
                    "description": _("Address"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Daily Lead",
                    "label": _("Daily Lead"),
                    "description": _("Daily Lead")
                },
                {
                    "type": "doctype",
                    "name": "Lead Per Organization",
                    "label": _("Lead Per Organization"),
                    "description": _("Lead Per Organization")
                },
                {
                    "type": "doctype",
                    "name": "Invoice Build Up",
                    "label": _("To Be Invoiced"),
                    "description": _("To Be Invoiced")
                }
            ]
        },
        {
            "label": _("Settings"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Campaign Setting",
                    "label": _("Campaign Setting"),
                    "description": _("Campaign Setting"),
                },
                {
                    "type": "doctype",
                    "name": "Industry Type",
                    "label": _("Main Industry"),
                    "description": _("Industry"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Sub Industry Type",
                    "label": _("Sub Industry"),
                    "description": _("Sub Industry Type"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Revenue Size",
                    "label": _("Revenue Size"),
                    "description": _("Revenue Size"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Employee Size",
                    "label": _("Employee Size"),
                    "description": _("Employee Size"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Campaign Types",
                    "label": _("Campaign Types"),
                    "description": _("Campaign Types"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Job Function",
                    "label": _("Job Function"),
                    "description": _("Job Function"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Level",
                    "label": _("Level"),
                    "description": _("Level"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Title",
                    "label": _("Title"),
                    "description": _("Title"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Campaign Department",
                    "label": _("Department"),
                    "description": _("Department"),
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Tool"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Organization Creation Tool",
                    "label": _("Organization Creation Tool"),
                    "description": _("Importing Organization Data"),
                },
            ]
        },
        {
            "label": _("Setup"),
            "items": [
                {
                    "type": "doctype",
                    "name": "LinkedIn User Setting",
                    "label": _("LinkedIn User Setting"),
                    "description": _("LinkedIn User Setting"),
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


