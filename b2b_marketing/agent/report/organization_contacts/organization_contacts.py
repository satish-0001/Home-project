# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six.moves import range
from six import iteritems
import frappe


field_map = {
	"Contact": [ "first_name", "last_name", "phone", "mobile_no", "email_id", "is_primary_contact" ],
	"Address": [ "address_line1", "address_line2", "city", "state", "pincode", "country", "is_primary_address" ]
}

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	party_type = "Campaign Organization"
	return [
		"{party_type}:Link/{party_type}".format(party_type=party_type),
		"Organization Name",
		"Address Line 1",
		"Address Line 2",
		"City",
		"State",
		"Postal Code",
		"Country",
		"Is Primary Address:Check",
		"First Name",
		"Last Name",
		"Phone",
		"Mobile No",
		"Email Id",
		"Is Primary Contact:Check"
	]
#
def get_data(filters):
	party_type = "Campaign Organization"
	party = filters.get("organization")

	return get_party_addresses_and_contact(party_type, party)

def get_party_addresses_and_contact(party_type, party):
	data = []
	filters = None
	party_details = frappe._dict()

	if not party_type:
		return []

	if party:
		filters = { "name": party }

	fetch_party_list = frappe.get_list(party_type, filters=filters, fields=["name","organization_name"], as_list=True)
	party_list = [d[0] for d in fetch_party_list]

	for d in party_list:
		party_details.setdefault(d, frappe._dict())

	party_details = get_party_details(party_type, party_list, "Address", party_details)
	party_details = get_party_details(party_type, party_list, "Contact", party_details)
	for party, details in iteritems(party_details):
		addresses = details.get("address", [])
		contacts  = details.get("contact", [])
		if not any([addresses, contacts]):
			org = frappe.get_doc("Campaign Organization",party)
			result = [party]
			result.append(org.organization_name)

			result.extend(add_blank_columns_for("Contact"))
			result.extend(add_blank_columns_for("Address"))
			data.append(result)
		else:
			addresses = list(map(list, addresses))
			contacts = list(map(list, contacts))

			max_length = max(len(addresses), len(contacts))
			for idx in range(0, max_length):
				result = [party]
				org = frappe.get_doc("Campaign Organization", party)
				result.append(org.organization_name)
				address = addresses[idx] if idx < len(addresses) else add_blank_columns_for("Address")
				contact = contacts[idx] if idx < len(contacts) else add_blank_columns_for("Contact")
				result.extend(address)
				result.extend(contact)

				data.append(result)
	return data

def get_party_details(party_type, party_list, doctype, party_details):
	filters =  [
		["Dynamic Link", "link_doctype", "=", party_type],
		["Dynamic Link", "link_name", "in", party_list]
	]
	fields = ["`tabDynamic Link`.link_name"] + field_map.get(doctype, [])

	records = frappe.get_list(doctype, filters=filters, fields=fields, as_list=True)
	for d in records:
		details = party_details.get(d[0])
		details.setdefault(frappe.scrub(doctype), []).append(d[1:])

	return party_details

def add_blank_columns_for(doctype):
	return ["" for field in field_map.get(doctype, [])]
