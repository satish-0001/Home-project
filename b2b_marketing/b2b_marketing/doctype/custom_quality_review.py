import frappe

@frappe.whitelist()
def call_update_fields(call):
    data = {}
    contact = frappe.get_value("Call", {"name": call}, "contact")
    if contact:
        data.update({"contact": contact})
        campaigns_contact = frappe.get_doc("Campaign Contact", {"name": contact})
        title = campaigns_contact.get("title", [])
        department = campaigns_contact.get("department", [])
        title_data = [tit.title for tit in title if tit]
        department_data = [dep.department for dep in department if dep]
        data.update({"department": department_data, "title": title_data})

    return data

@frappe.whitelist()
def contact_update(contact):
    data={}
    if contact:
        campaigns_contact = frappe.get_doc("Campaign Contact", {"name": contact})
        title = campaigns_contact.get("title", [])
        department = campaigns_contact.get("department", [])
        title_data = [tit.title for tit in title if tit]
        department_data = [dep.department for dep in department if dep]
        data.update({"department": department_data, "title": title_data})

    return data

