# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import json
from datetime import datetime
from frappe.utils import now_datetime, nowdate
from frappe import _, msgprint, throw
import requests

class Call(Document):
	@frappe.whitelist()
	def get_options(self, arg=None):
		if self.get("contact"):
			doc = frappe.get_doc("Campaign Contact", self.get("contact"))
			lst = {}
			st = ""
			if doc.phone:
				lst.update({"Phone":doc.phone})
			if doc.mobile_phone:
				lst.update({"Mobile Phone":doc.mobile_phone})
			if doc.corporate_phone:
				lst.update({"Corporate Phone":doc.corporate_phone})
			for number in lst:
				st += str(lst[number]) +  "({0})".format(number)+'\n'
			return st
	@frappe.whitelist()
	def update_agent_status(self):
		res = frappe.db.sql("""select TA.name from `tabAgents` TA
											  inner join `tabEmployee` TE on TA.employee = TE.name
											  inner join `tabUser` TU on TU.name =TE.user_id
											  where TU.name =%s limit 1""", (self.completed_by), as_dict=True)
		if res:
			for user in res:
				agent = frappe.get_doc("Agents", user.get("name"))
				if agent.total_calls:
					agent.total_calls = int(agent.total_calls) + 1
				else:
					agent.total_calls = 1
				agent.db_update()

@frappe.whitelist()
def create_lead(doc =None):
	call_id = frappe.get_doc("Call",doc)
	create_ld = False
	query1 = frappe.db.sql("""select name,number_of_lead,daily_cap from `tabDaily Lead` where date = %s and campaign = %s 
							  order by date desc limit 1""", (datetime.now().date(), call_id.campaign),as_dict=True)
	if query1:
		for s in query1:
			if s.get("daily_cap") > 0:
				if s.get("number_of_lead") >= s.get("daily_cap"):
					frappe.msgprint(_("Daily Limit Reached"))
					return False
				else:
					daily_lead = frappe.get_doc("Daily Lead", s.get("name"))
					daily_lead.number_of_lead = daily_lead.number_of_lead + 1
					daily_lead.save(ignore_permissions=True)
					create_ld = True
			else:
				daily_lead = frappe.get_doc("Daily Lead", s.get("name"))
				daily_lead.number_of_lead = daily_lead.number_of_lead + 1
				daily_lead.save(ignore_permissions=True)
				create_ld = True
	else:
		campaign = frappe.get_doc("Campaigns", call_id.campaign)
		daily_lead = frappe.new_doc("Daily Lead")
		daily_lead.campaign = call_id.campaign
		daily_lead.date = datetime.now().date()
		daily_lead.number_of_lead = 1
		daily_lead.daily_cap = campaign.daily_cap if campaign.daily_cap else 0
		daily_lead.call = call_id.name
		daily_lead.organization = call_id.organization
		daily_lead.contact = call_id.contact
		daily_lead.agent = call_id.agents_name
		daily_lead.supervisor = frappe.db.get_value('Campaigns', call_id.campaign, 'agent_name')
		daily_lead.call_date = nowdate()
		daily_lead.call_phone = call_id.call_phone
		daily_lead.mobile_phone = call_id.mobile_phone
		daily_lead.corporate_phone = call_id.corporate_phone
		daily_lead.organization_phone = call_id.organization_phone
		daily_lead.insert(ignore_permissions=True)
		create_ld = True

	if call_id.organization:
		result = frappe.get_all("Lead Per Organization",filters={"campaign": call_id.campaign,"organization": call_id.organization},fields=["name", "lead_per_organization", "lead_count"])
		if result:
			for r in result:
				if r.get('lead_per_organization') > 0:
					if r.get('lead_count') >= r.get('lead_per_organization'):
						frappe.msgprint(_("Organisation Limit Reached"))
						return False
					else:
						lead_org = frappe.get_doc("Lead Per Organization", r.get("name"))
						lead_org.lead_count = lead_org.lead_count + 1
						lead_org.save(ignore_permissions=True)
						create_ld = True
				else:
					lead_org = frappe.get_doc("Lead Per Organization", r.get("name"))
					lead_org.lead_count = lead_org.lead_count + 1
					lead_org.save(ignore_permissions=True)
					create_ld = True
		else:
			campaign = frappe.get_doc("Campaigns", call_id.campaign)
			lead_org = frappe.new_doc("Lead Per Organization")
			lead_org.campaign = call_id.campaign
			lead_org.organization = call_id.organization
			lead_org.lead_per_organization = campaign.lead_company_count if campaign.lead_company_count else 0
			lead_org.lead_count = 1
			lead_org.call = call_id.name
			lead_org.insert(ignore_permissions=True)
			create_ld = True
	if create_ld:
		lead = frappe.new_doc("Campaign Lead")
		lead.campaign = call_id.campaign
		lead.contact = call_id.contact
		lead.call = call_id.name
		# lead.get_email_phone_number()
		lead.insert(ignore_permissions=True)
		if frappe.db.get_single_value('Campaign Setting', 'lead_submitted'):
			lead.submit()
		call_id.campaign_lead = lead.name
		call_id.lead_create = 1
		call_id.call_disposal = "Lead Created"
		call_id.save(ignore_permissions=True)
		res = frappe.db.sql("""select TA.name from `tabAgents` TA
												  inner join `tabEmployee` TE on TA.employee = TE.name
												  inner join `tabUser` TU on TU.name =TE.user_id
												  where TU.name =%s limit 1""", (call_id.completed_by), as_dict=True)
		if res:
			for user in res:
				agent = frappe.get_doc("Agents", user.get("name"))
				if agent.success_rate and agent.total_calls:
					agent.success_rate_percentage = ((int(agent.success_rate)+1)/(int(agent.total_calls)+1))*100
					agent.success_rate = int(agent.success_rate) + 1

				else:
					agent.success_rate_percentage = (1/(int(agent.total_calls)+1)) * 100
					agent.success_rate = 1
				agent.db_update()

		build_invoice(charge_type="Charge Per Lead", doc_name=call_id.name,doc="Campaign Lead",voucher=lead.name)
		check_quality_review_in_camp_design(call_disposal = "Create Lead", doc_name = call_id.name,lead_name =lead.name)
	query1 = frappe.db.sql("""select name,campaign from `tabDaily Lead` where date = %s and campaign = %s
									and number_of_lead >= daily_cap and daily_cap > 0 order by date desc limit 1""",(datetime.now().date(), call_id.campaign), as_dict=True)
	if query1:
		for res in query1:
			call_ids = frappe.get_all("Call", filters={"status": "Scheduled","campaign":res.get('campaign')}, fields=['name'], as_list=1)
			for c_id in call_ids:
				x = frappe.get_doc("Call", c_id[0])
				x.is_daily_limit_reach = 1
				x.save(ignore_permissions=True)
	if call_id.organization:
		query2 = frappe.db.sql("""select name,campaign,organization from `tabLead Per Organization` 
								where campaign =%s and organization =%s and lead_count >= lead_per_organization and lead_per_organization > 0""",
								(call_id.campaign, call_id.organization), as_dict=True)
		if query2:
			for res in query2:
				call_ids = frappe.get_all("Call", filters={"status": "Scheduled", "campaign": res.get('campaign'),"organization":res.get('organization')},fields=['name'], as_list=1)
				for c_id in call_ids:
					x = frappe.get_doc("Call", c_id[0])
					x.is_organization_limit_reach = 1
					x.status = "Limit Reached"
					x.save(ignore_permissions=True)
	return True

@frappe.whitelist()
def open_assets(source_name,target_doc=None):
	def attach_assets(source,target):
		file_name =frappe.db.sql("""select name from `tabFile` where file_url =%s limit 1""",(source.attachment),as_dict=True)
		for fn in file_name:
			file_data = frappe.get_doc("File",fn.get('name'))
			_file = frappe.copy_doc(file_data)
			_file.update({"attached_to_doctype":"Call",
						  "attached_to_name":target.name})
			_file.insert(ignore_permissions=True)
			_file.reload()

	doclist = get_mapped_doc("Campaign Assets", source_name, {
		"Campaign Assets": {
			"doctype": "Call",
		}
	}, target_doc,attach_assets,ignore_permissions=True)
	return doclist

@frappe.whitelist()
def check_limit(doc =None):
	data = json.loads(doc)
	if data.get("campaign"):
		query2 =[]
		query1 =frappe.db.sql("""select name,campaign from `tabDaily Lead` where date = %s and campaign = %s
									and number_of_lead >= daily_cap and daily_cap > 0 order by date desc limit 1""",(datetime.now().date(),data['campaign']),as_dict=True)
		if query1:
			frappe.msgprint(_("Daily Limit Reached"))

		if 'organization' in data.keys():
			if data['organization']:
					query2 = frappe.db.sql("""select name,lead_per_organization,lead_count from `tabLead Per Organization` 
									where campaign =%s and organization =%s and lead_count >=lead_per_organization and lead_per_organization > 0""",(data['campaign'], data['organization']),as_dict=True)
					if query2:
						frappe.msgprint(_("Organisation Limit Reached"))
		if query1 or query2:
			return False
		else:
			time=now_datetime()
			return time

@frappe.whitelist()
def set_contact_dnc(doc_name =None):
	contact = frappe.get_doc("Campaign Contact",doc_name)
	contact.dnc = 1
	contact.save(ignore_permissions=True)

@frappe.whitelist()
def set_contact_wrong_number(doc_name =None):
	contact = frappe.get_doc("Campaign Contact",doc_name)
	contact.wrong_number = 1
	contact.save(ignore_permissions=True)

@frappe.whitelist()
def check_quality_review_in_camp_design(call_disposal = None, doc_name = None,lead_name=None):
	call = frappe.get_doc("Call", doc_name)
	query_result = frappe.db.sql("""select tcc.trigger_section,tcc.quality_goal from `tabCampaigns Quality Child` as tcc 
									inner join `tabCampaigns Designer` as tcd on tcc.parent = tcd.name 
									inner join `tabCampaigns` as tc on tc.campaigns_name = tcd.name 
									where tc.name =%s and tcc.trigger_section = %s limit 1""",(call.campaign,call_disposal),as_dict=True)
	for res in query_result:
		quality_review = frappe.new_doc("Quality Review")
		quality_review.goal = res.get("quality_goal")
		if call_disposal == "Create Lead":
			quality_review.quality_type = "Campaign Lead"
			quality_review.value = lead_name
		else:
			quality_review.quality_type = "Call"
			quality_review.value = call.name
		quality_review.campaign = call.campaign
		quality_review.contact = call.contact
		agent = frappe.db.sql("""select TA.name from `tabAgents` TA
														  inner join `tabEmployee` TE on TA.employee = TE.name
														  inner join `tabUser` TU on TU.name =TE.user_id
														  where TU.name =%s limit 1""", (call.completed_by))
		if agent:
			quality_review.agent = agent[0][0]
		quality_review.date = datetime.now().date()
		q1 =frappe.db.sql("""select objective,target from `tabQuality Goal Objective` where parent =%s""",(res.get("quality_goal")),as_dict=True)
		for s in q1:
			quality_review.append("reviews", {
				"objective" :s.get("objective"),
				"target" : s.get("target")
			})
		quality_review.insert(ignore_permissions=True)

@frappe.whitelist()
def build_invoice(charge_type =None,doc_name=None,doc =None,voucher =None):
	call = frappe.get_doc("Call", doc_name)
	query = frappe.db.sql("""select tcd.name as designer_name,
							 tc.name as campaign,
							 tcd.customer_name,
							 tcd.agent_name,
							 tcd.invoice_policy,
							 tcd.invoicing_frequency,
							 tcd.lead_call_fixed_price,
							 tcd.cost_center from `tabCampaigns Designer` as tcd 
							 inner join `tabCampaigns` as tc on tc.campaigns_name = tcd.name 
							 where tc.name =%s and tcd.invoice_policy =%s""",(call.campaign,charge_type),as_dict=True)
	item =''
	if charge_type == "Charge Per Lead":
		item = frappe.db.get_single_value('Campaign Setting', 'lead_item')
	if charge_type == "Charge Per Call":
		item = frappe.db.get_single_value('Campaign Setting', 'call_item')

	res = frappe.db.sql("""select TA.name from `tabAgents` TA
												  inner join `tabEmployee` TE on TA.employee = TE.name
												  inner join `tabUser` TU on TU.name =TE.user_id
												  where TU.name =%s limit 1""", (call.completed_by))
	agent =''
	if res:
		agent = res[0][0]

	for res in query:
		inv_build = frappe.new_doc("Invoice Build Up")
		inv_build.campaigns = res.get('campaign')
		inv_build.campaigns_name = res.get('designer_name')
		inv_build.customer = res.get('customer_name')
		inv_build.based_on = doc
		inv_build.voucher = voucher
		inv_build.charge = res.get('lead_call_fixed_price')
		inv_build.status = "To Bill"
		inv_build.invoicing_frequency = res.get('invoicing_frequency') if res.get('invoicing_frequency') else None
		inv_build.supervisor = res.get('agent_name')
		inv_build.agent = agent if agent else None
		inv_build.cost_center = res.get('cost_center')
		inv_build.item = item
		inv_build.date = datetime.now().date()
		inv_build.transaction_date = datetime.now().date()
		inv_build.insert(ignore_permissions=True)


@frappe.whitelist()
def get_campaign_script(doc_name =None):
	camp =frappe.get_doc("Campaigns",doc_name)
	return camp.script

@frappe.whitelist()
def create_new_call(doc_name =None):
	old_call = frappe.get_doc("Call",doc_name)
	call = frappe.new_doc("Call")
	call.campaign = old_call.campaign
	call.contact = old_call.contact
	call.organization = old_call.organization if old_call.organization else None
	call.call_allocation = old_call.call_allocation
	call.scheduled_queue = old_call.scheduled_queue
	# call.survey = old_call.survey
	call.campaigns_name = old_call.campaigns_name
	call.parent_call = doc_name
	call.agent=old_call.agents_name
	# call.get_email_phone_number()
	call.insert(ignore_permissions=True)
	return True

# --------Quality Reviews DocType Method----------------------create Record is submittable --------------------------
# @frappe.whitelist()
# def set_submittable_property(quality,method):
# 	print("----------------quality",quality)
# 	frappe.make_property_setter({'doctype': 'Quality Review', 'doctype_or_field': 'DocType', 'value': '1', 'property': 'is_submittable','property_type': 'Check'})

# ------------------------------set rating------------------------------------------------------------

@frappe.whitelist()
def set_quality_rating(doc_name = None,result = None):
	quality = frappe.get_doc("Quality Review",doc_name)
	if quality:
		if quality.quality_type and quality.value:
			query = frappe.db.sql("""select avg(quality_rating) as avg_rating from `tabQuality Review Objective` 
									where parenttype ='Quality Review' and parent=%s""",(quality.name),as_dict=True)
			
			for s in query:
				org = frappe.get_doc(quality.quality_type, quality.value)
				if org.quality_rating:
					org.quality_rating = (org.quality_rating + s.get("avg_rating"))/2
				else:
					org.quality_rating = s.get("avg_rating")

				if org.quality_views:
					org.quality_views += 1
				else:
					org.quality_views = 1

				org.last_quality_date = datetime.now().date()
				
				if quality.quality_type == 'Call':
					org.quality_result = quality.result
				org.db_update()

				if quality.quality_type == "Call":
					res = frappe.db.sql("""select TA.name from `tabAgents` TA
										inner join `tabEmployee` TE on TA.employee = TE.name
										inner join `tabCall` TC on TC.completed_by =TE.employee_name
										where TC.name =%s""", (quality.value), as_dict=True)
					if res:
						for user in res:
							agent = frappe.get_doc("Agents", user.get("name"))
							if agent:
								agent.last_update_on=datetime.now().date()

							if agent.quality_rating:
								agent.quality_rating = (agent.quality_rating + s.get("avg_rating"))/2
							else:
								agent.quality_rating = s.get("avg_rating")

							if agent.quality_views:
								agent.quality_views += 1
							else:
								agent.quality_views = 1
											
							agent.db_update()

@frappe.whitelist()
def send_email(doc_name =None):
	doc = frappe.get_doc("Call", doc_name)
	
	file = []
	data = { "email_template": None,
			 "subject": None,
			 "content": None,
			 "attachment": [],
			 "recipients": None,
			 "sender": None,
			 "sender_name": None
			}
	query = frappe.db.sql("""select TCD.name,TCD.email_template from `tabCampaigns Designer` TCD
							inner join `tabCampaigns` TC on TC.campaigns_name = TCD.name where TC.name =%s""",(doc.campaign),as_dict=True)
	print("hvugfyyugdugdgdfiu",query)
	for s in query:
		if s.email_template:
			e_temp = frappe.get_doc("Email Template",s.email_template)
			data["email_template"] = s.email_template
			print(frappe.render_template(e_temp.response,doc.__dict__))
			data["subject"] = frappe.render_template(e_temp.subject,doc.__dict__)
			data["content"] = frappe.render_template(e_temp.response,doc.__dict__)
			files = frappe.db.sql("""select name from `tabFile` where attached_to_doctype ="Email Template" and attached_to_name =%s""",(s.email_template),as_dict=True)
			for f in files:
				file.append(f.name)
			print("&&&&&&&&&&&",file)
			data["attachment"] = file
		else:
			frappe.throw(_("Please first set the Email Template in Campaign Designer"))

	contact = frappe.db.sql("select email from `tabCampaign Contact` where name =%s",(doc.contact))
	print("contact------------------",contact)
	if contact:
		data["recipients"] = contact[0][0]
	else:
		frappe.throw(_("Please set primary email in Contact"))

	user_email = frappe.get_doc("User",frappe.session.user)
	data['sender'] = user_email.email
	data['sender_name'] = frappe.session.user
	
	return data


@frappe.whitelist()
def get_assest_data(doc_name =None):
	doc = frappe.get_doc("Call", doc_name)
	if doc.campaigns_name:
		co=frappe.get_doc("Campaigns Designer",doc.campaigns_name)
		
		return co.assets


@frappe.whitelist()
def send_assets(doc_name =None,assest=None):
	if assest:
		doc = frappe.get_doc("Call", doc_name)
		file = []
		if doc.campaigns_name:
			co=frappe.get_doc("Campaigns Designer",doc.campaigns_name)
			
			if len(co.assets):
				for i in co.assets:
					if i.name in assest:
						data = { "email_template": None,
								"subject": None,
								"content": None,
								"attachment": [],
								"recipients": None,
								"sender": None,
								"sender_name": None
								}
						
							
						data["subject"] = frappe.render_template(i.email_subject,doc.__dict__)
						data["content"] = frappe.render_template(i.description,doc.__dict__)
						if i.attachment:
							attcFile=frappe.db.get_value("File",{"file_url":i.attachment},["name"])
							data["attachment"]=[attcFile]
							

						contact = frappe.db.sql("select email from `tabCampaign Contact` where name =%s",(doc.contact))
						if contact:
							data["recipients"] = contact[0][0]
						else:
							frappe.throw(_("Please set primary email in Campaign Contact"))

						user_email = frappe.get_doc("User",frappe.session.user)
						data['sender'] = user_email.email
						data['sender_name'] = frappe.session.user
						file.append(data)
			return file
	else:
		frappe.throw(_("Please first set the Assest in Campaign Designer"))
	
@frappe.whitelist()
def select_call(doc_name = None):
	doc = frappe.get_doc("Contact", doc_name)
	lst = []
	st = ""
	for number in doc.phone_nos:
		lst.append(number.phone)
	for number in set(lst):
		st += str(number)+'\n'
	fields = [{
			"label": "Number",
			"fieldname": "phone_number",
			"fieldtype": "Select",
			"options": st,
			"default":lst[0] if lst else None,
			"reqd": 1,
		},
		{
			"label": "Call",
			"fieldname": "call",
			"fieldtype": "Button",
		},
	]
	return fields

@frappe.whitelist()
def make_call(doc_name =None,dest_number = None):
	# ------------------   Twilio Settings  -------------------
	import os
	from twilio.rest import Client
	twilio_settings = frappe.get_doc("Twilio Settings")
	enable = frappe.db.get_single_value('Twilio Settings', 'enabled')
	account_sid = frappe.db.get_single_value('Twilio Settings', 'account_sid')
	auth_token = twilio_settings.get_password(fieldname="auth_token", raise_exception=False)
	if enable:
		client = Client(account_sid, auth_token)
		call = client.calls.create(
			to=dest_number,
			from_='+14048009373',
			url='http://demo.twilio.com/docs/voice.xml'
		)
	else:
		frappe.throw(_("Please enable the Api"))
# ----------------------Quality Review---------------

@frappe.whitelist()
def get_campaign_customer_contact(quality_type = None, value= None,doc_name =None):
	doc = frappe.get_doc("Quality Review", doc_name)
	if quality_type and value:
		if quality_type in ['Campaign Lead', 'Call']:
			table_name = "tab"+quality_type
			query = """select TCD.customer_name,TC.name,QR.contact from `{0}` QR 
									inner join `tabCampaigns` TC on QR.campaign = TC.name
									inner join `tabCampaigns Designer` TCD on TC.campaigns_name = TCD.name 
									where QR.name ='{1}'""".format(table_name,value)
			result = frappe.db.sql(query, as_dict=True)
			if result:
				doc.campaign = result[0].get("name")
				doc.customer = result[0].get("customer_name")
				doc.contact = result[0].get("contact")
				doc.db_update()
	return True


@frappe.whitelist()
def update_ct_org(contact,organization,values,doc_id):
	cc_fields = ["first_name", "last_name", "title", "department", "email", "corporate_phone", "mobile_phone", "phone"]
	org_fields = ["name", "employees", "annual_revenue", "industry", "sub_industry", "website", "domain"]
	if values:
		values = json.loads(values)
		call_doc = frappe.get_doc("Call", doc_id)
	cc_doc = frappe.get_doc("Campaign Contact", contact)
	og_doc = frappe.get_doc("Campaign Organization", organization)
	for field in cc_fields:
		if field in values:
			if field in cc_fields:
				call_doc.db_set(field, values[field])
				cc_doc.set(field, values[field])
	for field in org_fields:
		if field in values:
			if field in org_fields:
				call_doc.db_set(field, values[field])
				og_doc.set(field, values[field])
	cc_doc.save()
	og_doc.save()


@frappe.whitelist()
def update_callcamp_ct_org(contact,organization,values,doc_id):
	return_value = []
	cc_fields = ["first_name", "last_name","department", "email", "corporate_phone", "mobile_phone", "phone"]
	org_fields = ["employees", "annual_revenue", "industry", "website", "domain"]
	if values:
		values = json.loads(values)
		call_doc = frappe.get_doc("Call", doc_id)
	cc_doc = frappe.get_doc("Campaign Contact", contact)
	og_doc = frappe.get_doc("Campaign Organization", organization)
	for field in cc_fields:
		if field in values:
			if field in cc_fields:
				return_value.append({field:values[field]})
				call_doc.db_set(field, values[field])
				cc_doc.set(field, values[field])
	for field in org_fields:
		if field in values:
			if field in org_fields:
				return_value.append({field:values[field]})
				call_doc.db_set(field, values[field])
				og_doc.set(field, values[field])
	cc_doc.save()
	og_doc.save()
	return return_value
			



