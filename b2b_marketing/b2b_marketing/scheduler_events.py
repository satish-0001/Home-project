from __future__ import unicode_literals
import json
import frappe
from datetime import datetime

def auto_change_campaign_status():
    query = """ select name from `tabCampaigns` where status='Running' and expected_end < '{0}' and expected_end is not Null """.format((datetime.now().date()))
    campaigns = frappe.db.sql(query, as_dict=True)
    for campaign in campaigns:
        doc = frappe.get_doc("Campaigns", campaign.get("name"))
        doc.status = "Past Due"
        doc.flags.ignore_permissions = True
        doc.flags.ignore_mandatory = True
        doc.save(ignore_permissions=True)

def reset_daily_limit_reach():
	query =frappe.db.sql("""select name  from `tabCall` where status="Scheduled" and is_daily_limit_reach = 1""",as_dict=True)
	for res in query:
		call = frappe.get_doc("Call", res.get("name"))
		call.is_daily_limit_reach = 0
		call.save(ignore_permissions=True)

def daily_invoice_build():
	build_invoice_schedular(invoicing_frequency ="Daily")

def weekly_invoice_build():
	build_invoice_schedular(invoicing_frequency ="Weekly")

def monthly_invoice_build():
	build_invoice_schedular(invoicing_frequency ="Monthly")

def build_invoice_schedular(invoicing_frequency =None):
	query = frappe.db.sql("""select tcd.name as designer_name,
							 tc.name as campaign,
							 tcd.customer_name,
							 tcd.agent_name,
							 tcd.invoice_policy,
							 tcd.invoicing_frequency,
							 tcd.lead_call_fixed_price, 
							 tcd.cost_center from `tabCampaigns Designer` as tcd 
							 inner join `tabCampaigns` as tc on tc.campaigns_name = tcd.name 
							 where tcd.invoice_policy ='Fixed Charge' and tc.status ='Running'
							 and tcd.invoicing_frequency =%s""",(invoicing_frequency),as_dict=True)
	item = frappe.db.get_single_value('Campaign Setting', 'fixed_item')
	for res in query:
		inv_build = frappe.new_doc("Invoice Build Up")
		inv_build.campaigns = res.get('campaign')
		inv_build.campaigns_name = res.get('designer_name')
		inv_build.customer = res.get('customer_name')
		inv_build.charge = res.get('lead_call_fixed_price')
		inv_build.status = "To Bill"
		inv_build.invoicing_frequency = res.get('invoicing_frequency')
		inv_build.supervisor = res.get('agent_name')
		inv_build.cost_center = res.get('cost_center')
		inv_build.item = item
		inv_build.date = datetime.now().date()
		inv_build.transaction_date = datetime.now().date()
		inv_build.insert(ignore_permissions=True)

# this is scheduler executes daily
def daily_get_contact_list_update():
	all_camps = frappe.db.get_all("Campaigns",
								  fields=['name','campaigns_name','campaigns_designer_filter'],
								  filters={'status':['=','Running']})
	for data in all_camps:

		self_doc = frappe.get_doc("Campaigns Designer", data.campaigns_name)

		if data.campaigns_designer_filter:
			res = json.loads(data.campaigns_designer_filter)
		else:
			res = {}
		res['dnc'] = ['=', '0']
		res['is_b2b_contact'] = ['=', '1']
		resulted_contact = []
		allowed_contact = []
		contact_suppression = []
		organization_suppression = []
		abm_list = []
		for row in self_doc.contract_suppression:
			contact_suppression.append(row.email)
		for row in self_doc.company_suppression:
			organization_suppression.append(row.domain)
		for row in self_doc.abm_list:
			abm_list.append(row.domain)
		# for excepted contact by mail id
		if contact_suppression:

			excepted_contact_supp = frappe.get_all("Contact Email",
										  filters={'email_id':['in',contact_suppression]},
										  fields=['parent'])
			for e_cont in excepted_contact_supp:
				resulted_contact.append(e_cont.parent)

		# for excepted contact by domain
		if organization_suppression:
			os_len = len(organization_suppression)
			count = 0
			str = "("
			for ele in organization_suppression:
				count += 1
				if count != os_len:
					str += '"'+ele+'",'
				else:
					str += '"'+ele+'")'
			org_list = []
			excepted_contact_org = frappe.db.sql("""select name from `tabOrganization` where domain in {0} """.format(str),as_dict=1)
			for org in excepted_contact_org:
				org_list.append(org.name)

			excepted_contact_supp = frappe.get_all("Contact",
												   filters={'organization': ['in', org_list]},
												   fields=['name'])
			for e_cont in excepted_contact_supp:
				resulted_contact.append(e_cont.name)

		# for allowed contact by domain
		if abm_list:
			os_len = len(abm_list)
			count = 0
			str = "("
			for ele in abm_list:
				count += 1
				if count != os_len:
					str += '"'+ele+'",'
				else:
					str += '"'+ele+'")'
			org_list = []
			excepted_contact_org = frappe.db.sql(
				"""select name from `tabOrganization` where domain in {0} """.format(str),
				as_dict=1)
			for org in excepted_contact_org:
				org_list.append(org.name)

			allowed_contact_supp = frappe.get_all("Contact",
												   filters={'organization': ['in', org_list]},
												   fields=['name'])
			for e_cont in allowed_contact_supp:
				allowed_contact.append(e_cont.name)
		print("---------------------------allowed connatc",allowed_contact)
		if resulted_contact:
			print("*************resulted_contact",resulted_contact)
			res['name'] = ['not in', resulted_contact]
		if allowed_contact:
			res['name'] = ['in', allowed_contact]

		filters = frappe._dict(res)
		print("--------------------------------------filters",filters)
		contacts = frappe.get_all("Contact", filters=filters, fields=['name'], as_list=1)
		print("----------------------------contact",contacts,len(contacts))
		self_doc.contact_list = []
		total_available_contacts = len(contacts)
		return_list = []
		for result in contacts:
			if frappe.db.exists("Contact",result[0]):
				cont = frappe.get_doc('Contact', result[0])
				# total_available_contacts = result[1]
				if cont:
					dict = {'contact':cont.name,
							"organization": cont.organization if cont.organization else None,
							"mobile": cont.mobile_no if cont.mobile_no else None,
							"phone": cont.phone if cont.phone else None,
							'email': cont.email_id if cont.email_id else None,
							'total_available_contacts':total_available_contacts}
					return_list.append(dict)
					# self_doc.append("contact_list", {
					# 	"contact": cont.name,
					# 	"organization": cont.organization if cont.organization else None
					# })

		campaigns_doc = frappe.get_doc("Campaigns",data.name)
		camp_doc_contact = []
		status_updation = 0
		for row in campaigns_doc.contact_list:
			camp_doc_contact.append(row.contact)
		for data in return_list:

			if data['contact'] not in camp_doc_contact:
				status_updation = 1
				campaigns_doc.append('contact_list',{
					"contact" : data['contact'],
					"organization" : data['organization'],
					"phone" : data['phone'],
					"mobile" : data['mobile'],
					"email" : data['email']
				})
		if status_updation == 1:
			campaigns_doc.status = "To Start"
		campaigns_doc.save(ignore_permissions=True)