# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from datetime import datetime
import json
from datetime import timedelta
from frappe.utils import cstr
from frappe.utils.data import flt, getdate
from frappe.utils.background_jobs import enqueue

class CampaignsDesigner(Document):
	def autoname(self):
		self.name = str(self.customer_name) + " [" + str(self.campaign_name)+"]"

	def validate(self):
		lst = []
		for row in self.assets:
			lst.append(row.email_subject)
		if len(lst) != len(set(lst)):
			frappe.throw("Duplicate Asset Title Not Allowed")

	def before_update_after_submit(self):
		new_email_list=[]
		campaign_designer = frappe.get_doc("Campaigns Designer", self.name)
		campaign_desire = campaign_designer.max_number_of_contacts + flt(self.max_number_of_contacts)
		self.db_set('max_number_of_contacts', campaign_desire, notify=True)

		filters = self.filters
		data = get_contact_list(filters, name=self.name, doc=self)
		data1 = self.contact_filters
		total_len = len(data) - 1
		self.db_set('total_available_contacts', total_len, notify=True)

		doc_name = frappe.get_list("Campaigns", filters={"campaigns_name": self.name}, fields=["name"])
		if doc_name:
			campaigns = frappe.get_doc("Campaigns", doc_name[0].name)
			if isinstance(data1, str):
				data1 = json.loads(data1)
			else:
				data1 = data1 or []
			existing_contacts = {con.get('contact') for con in data1 if con.get('contact')}
			
			new_contacts = []
			for contact in data: 
				if contact.get('contact') and contact.get('contact') not in existing_contacts:
					new_email_list.append(contact.get('email'))
					new_contacts.append({
						'contact': contact.get('contact'),
						'organization': contact.get('organization'),
						'phone': contact.get('phone'),
						'mobile': contact.get('mobile'),
						'email': contact.get('email'),
						'corporate_phone': contact.get('corporate_phone'),
						'organization_contact': contact.get('organization_contact')
					})
					existing_contacts.add(contact.get('contact'))

			updated_data1 = data1 + new_contacts
			self.db_set('contact_filters', json.dumps(updated_data1), notify=True)

			for contact in new_contacts:
				campaigns.append('contact_list', contact)
			
			campaigns.save()
		enqueue(method=self.send_email, queue='long', timeout=6000, new_email_list=new_email_list)
		# self.send_email(new_email_list,batch_size=100)


	@frappe.whitelist()
	def send_email(self,new_email_list,batch_size=100):
		new_email_list = [email for email in new_email_list if email]
		file = []
		data = {
			"subject": None,
			"content": None,
			"attachments": [],
			"recipients": [],
			"sender": None,
		}
		if self.email_template:
			e_temp = frappe.get_doc("Email Template", self.email_template)
			data["subject"] = frappe.render_template(e_temp.subject)
			data["content"] = frappe.render_template(e_temp.response)
			files = frappe.db.sql("""select name from `tabFile` where attached_to_doctype ="Email Template" and attached_to_name =%s""", (self.email_template), as_dict=True)
			for f in files:
				file.append(f.name)
			data["attachments"] = file
		else:
			frappe.throw(_("Please first set the Email Template in Campaign Designer"))

		# user_email = frappe.get_doc("User", frappe.session.user)
		# data['sender'] = f"{frappe.session.user} <{user_email.email}>"
		data['sender'] = self.user_email_id

		for i in range(0, len(new_email_list), batch_size):
			batch_recipients = new_email_list[i:i + batch_size]
			data['recipients'] = batch_recipients
			frappe.sendmail(
				recipients=data['recipients'],
				subject=data['subject'],
				message=data['content'],
				attachments=data['attachments'],
				reference_doctype=self.doctype,
				reference_name=self.name,
				expose_recipients="header",
				sender=data['sender']
			)
			frappe.db.commit()


	@frappe.whitelist()
	def set_sub_agents(self):
		to_remove = []
		for s in self.get("agents_list"):
			to_remove.append(s)
		for d in to_remove:
			self.remove(d)
		agents = frappe.db.sql("""select agents_name,success_rate_percentage,total_calls,quality_rating from `tabAgents` where parent_agents = '{0}'""".format(self.agent_name),as_dict=1)
		for k in agents:
			self.append("agents_list", {'agent':k.agents_name,
			'success_rate': str(k.get("success_rate_percentage"))+"%",
			'total_calls': k.total_calls,
			'quality_rating': k.quality_rating})
	
	@frappe.whitelist()
	def on_submit(self):
		if not self.agents_list:
			frappe.throw("Minimum one Agent is required to Submit the Campaigns Designer.")
		emails = self.get_contract_emails()
		domain = self.get_organization_domain()
		abm_domain = self.get_abm_domain()
		campaign = self.create_campaigns()
		self.create_contact(campaign,emails,domain,abm_domain)
		self.create_assets(campaign)
		if campaign:
			campaign.save(ignore_permissions=True)
			return True

	@frappe.whitelist()
	def get_cal(self):
		a=frappe.db.get_value("Campaigns",{'campaigns_name':self.name,'status':["!=","Cancelled"]},['name'])
		if not a:
			return True
		m=frappe.get_all("Campaigns",{"campaigns_name":self.name})
		if len(m)==0:
			return True


	def create_campaigns(self):
		lng =len(self.agents_list)
		camp = frappe.new_doc("Campaigns")
		camp.campaigns_name = self.name
		camp.company = self.company
		camp.total_available_contacts = self.total_available_contacts
		camp.agent_name = self.agent_name
		camp.status = 'To Start'
		camp.expected_start = self.start_on
		camp.expected_end = self.end_on
		camp.delivery_target = self.delivery_target
		camp.daily_cap = self.daily_cap
		camp.lead_company_count = self.lead_company_count
		camp.start_on = datetime.now()
		camp.number_of_agents = lng
		camp.script_template = self.script_template if self.script_template else None
		camp.script = self.script if self.script else None
		for row in self.agents_list:
			camp.append('agents_list',{
				'agent':row.agent,
				'success_rate_percentage': row.success_rate,
				'total_calls': row.total_calls,
				'quality_rating': row.quality_rating
			})

		return camp

	def create_assets(self,camp):
		for ass in self.get("assets"):
			camp.append("assets", {
								
				"attachment":ass.attachment,
				"email_subject":ass.email_subject+str(1),
				"description":ass.description,
				"transaction_date":datetime.now().date()
			})
		return True

	def create_contact(self,campaign,emails = None,domain = None,abm_domain = None):						#Create Contact base on pyhton codition
		cont_lst = []
		if domain:
			if len(domain) >1:
				query=""" select DISTINCT(tc.name) from `tabCampaign Contact` tc 
						inner join `tabOrganization` tbo on tbo.name = tc.organization 
						where tbo.domain in {0}""".format(tuple(domain))
			else:
				query=""" select DISTINCT(tc.name) from `tabCampaign Contact` tc 
						inner join `tabOrganization` tbo on tbo.name = tc.organization 
						where tbo.domain = {0}""".format(domain[0])
			contact = frappe.db.sql(query)
			for a in contact:
				cont_lst.append(a[0])
		if emails:
			if len(emails) >1:
				query1 ="""select DISTINCT(tc.name) from `tabCampaign Contact` tc 
							where tc.email in {0} or tc.additional_email in {1}""".format(tuple(emails),tuple(emails))
			else:
				query1 = """select DISTINCT(tc.name) from `tabCampaign Contact` tc 
											where tc.email = '{0}' or tc.additional_email = '{0}'""".format(emails[0])
			eml = frappe.db.sql(query1)
			for e in eml:
				if e[0] not in cont_lst:
					cont_lst.append(e[0])
		abm_lst =[]
		if abm_domain:
			if len(abm_domain) >1:
				query2 =""" select DISTINCT(tc.name) from `tabCampaign Contact` tc 
						inner join `tabOrganization` tbo on tbo.name = tc.organization 
						where  tbo.domain in {0}""".format(tuple(abm_domain))
			else:
				query2 =""" select DISTINCT(tc.name) from `tabCampaign Contact` tc 
						inner join `tabOrganization` tbo on tbo.name = tc.organization 
						where  tbo.domain = '{0}' """.format(abm_domain[0])
			abm = frappe.db.sql(query2)
			for a in abm:
				abm_lst.append(a[0])
		if abm_lst:
			for x in cont_lst:
				if x in abm_lst:
					abm_lst.remove(x)

		for s in self.get("contact_list"):
			if abm_lst:
				if s.contact in abm_lst:
					campaign.append("contact_list", {
						"contact": s.contact,
						"organization": s.organization if s.organization else None,
						'email':s.email if s.email else None,
						'mobile':s.mobile if s.mobile else None,
						'phone':s.phone if s.phone else None
					})
			elif cont_lst:
				if s.contact not in cont_lst:
					campaign.append("contact_list", {
						"contact": s.contact,
						"organization": s.organization if s.organization else None,
						'email': s.email if s.email else None,
						'mobile': s.mobile if s.mobile else None,
						'phone': s.phone if s.phone else None
					})
			else:
				campaign.append("contact_list", {
					"contact": s.contact,
					"organization": s.organization if s.organization else None,
					'email': s.email if s.email else None,
					'mobile': s.mobile if s.mobile else None,
					'phone': s.phone if s.phone else None
				})
		return True

	def get_contract_emails(self):
		lst =[]
		for cont in self.get("contract_suppression"):
			lst.append(cont.email)
		return lst

	def get_organization_domain(self):
		lst =[]
		for cont in self.get("company_suppression"):
			lst.append(cont.domain)
		return lst

	def get_abm_domain(self):
		lst =[]
		for cont in self.get("abm_list"):
			lst.append(cont.domain)
		return lst

	def on_cancel(self):									#Cancel Campaign
		campaigns = frappe.db.sql("""select name,status from `tabCampaigns` where campaigns_name = %s""",(self.name))
		for camp in campaigns:
			if camp[1]!= "To Start":
				frappe.throw(_("You cannot cancel a submitted Campaign Designer record if it has ongoing or cancelled Campaigns. Only Campaigns with status To Start can be deleted."))
			else:
				frappe.db.sql("""update `tabCampaigns` set status = 'Cancelled' where name = %s""", (camp[0]))

@frappe.whitelist()
def get_days(start_date=None,end_date=None,company=None):
	days = 0.0
	holiday_list = ''
	if start_date and end_date:
		if not holiday_list:
			holiday_list = frappe.db.get_value('Company', company, "default_holiday_list")

		if not holiday_list:
			frappe.throw(_('Please set a default Holiday List for Company {0}').format( company))

		holidays=frappe.db.get_all("Holiday",{"parent":holiday_list,"holiday_date":["between",[getdate(start_date),getdate(end_date)]]},["holiday_date"])
		
		holidays = [getdate(i.get("holiday_date"))for i in holidays]

		if start_date and end_date:
			d1 = datetime.strptime(start_date, "%Y-%m-%d")
			d2 = datetime.strptime(end_date, "%Y-%m-%d")
			days = (d2-d1).days+1 or 0.0
		days -= len(holidays)
	return days

@frappe.whitelist()
def update_contact_list(filters,self):
	# try:

	self_doc = frappe.get_doc("Campaigns Designer", self)
	camps = frappe.db.get_all("Campaigns",
							  fields=['name'],
							  filters={'campaigns_name':['=',self_doc.name]})
	if filters:
		res = json.loads(filters)
	else:
		res = {}
	res['dnc'] = ['=', '0']
	res['wrong_number'] = ['=','0']
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

		excepted_contact_supp = frappe.get_all("Campaign Contact",
									  filters={'email':['in',contact_suppression]},
									  fields=['name'])
		for e_cont in excepted_contact_supp:
			resulted_contact.append(e_cont.name)

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
		excepted_contact_org = frappe.db.sql("""select name from `tabCampaign Organization` where domain in {0} """.format(str),as_dict=1)
		for org in excepted_contact_org:
			org_list.append(org.name)

		excepted_contact_supp = frappe.get_all("Campaign Contact",
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
			"""select name from `tabCampaign Organization` where domain in {0} """.format(str),
			as_dict=1)
		for org in excepted_contact_org:
			org_list.append(org.name)

		allowed_contact_supp = frappe.get_all("Campaign Contact",
											   filters={'organization': ['in', org_list]},
											   fields=['name'])
		for e_cont in allowed_contact_supp:
			allowed_contact.append(e_cont.name)

	if resulted_contact:

		res['name'] = ['not in', resulted_contact]
	if allowed_contact:
		res['name'] = ['in', allowed_contact]

	filters = frappe._dict(res)
	if filters.get("department"):
		del filters['department']

	if filters.get("title"):
		del filters['title']
	
	if filters.get("keywords"):
		del filters['keywords']
	contacts = frappe.get_all("Campaign Contact", filters=filters, fields=['name'], as_list=1)

	self_doc.contact_list = []
	total_available_contacts = len(contacts)
	return_list = []
	for result in contacts:
		if self_doc.max_number_of_contacts:
			if len(return_list)==self_doc.max_number_of_contacts:
				break
		tot=0
		if filters.get("department"):
			val=frappe.db.get_value("Department Table",{"department":filters.get("department"),"parent":result[0]},["name"])
			if val:
				tot+=1
		else:
			tot+=1

		if filters.get("title"):
			val=frappe.db.get_value("Title Table",{"title":filters.get("title"),"parent":result[0]},["name"])
			if val:
				tot+=1
		else:
			tot+=1

		if filters.get("keywords"):
			val=frappe.db.get_value("Title Table",{"keywords":filters.get("keywords"),"parent":result[0]},["name"])
			if val:
				tot+=1
		else:
			tot+=1
		if tot==3:
			if frappe.db.exists("Campaign Contact",result[0]):
				cont = frappe.get_doc('Campaign Contact', result[0])
				if cont:
					dict = {'contact':cont.name,
							"organization": cont.organization if cont.organization else None,
							"mobile": cont.mobile_phone if cont.mobile_phone else None,
							"phone": cont.phone if cont.phone else None,
							'email': cont.email if cont.email else None
							}
					return_list.append(dict)
		# 			processed_count += 1
		# if self_doc.max_number_of_contacts and processed_count >= self_doc.max_number_of_contacts:
		# 	break

	for row in camps:
		camp_obj = frappe.get_doc("Campaigns",row.name)
		if camp_obj.status == "Completed":
			frappe.msgprint("Campaign :"+row.name+" Is Completed Cannot Update Contact ")
		lst_contact = []
		if camp_obj.prospect_order == "Random":
			for row in camp_obj.contact_list:
				lst_contact.append(row.contact)
		else:
			for row in camp_obj.contact_list:
				lst_contact.append(row.contact)
		for data in return_list:
			if data['contact'] not in lst_contact:
				camp_obj.append('contact_list',{
					'contact': data['contact'],
					"organization": data["organization"] if data["organization"] else None,
					"mobile": data['mobile'] if data['mobile'] else None,
					"phone": data['phone'] if data['phone'] else None,
					'email': data['email'] if data['email'] else None,
				})
		cont_total = len(camp_obj.get("contact_list"))
		diff=flt(cont_total)-flt(camp_obj.total_available_contacts)
		camp_obj.total_available_contacts = cont_total
		self_doc.db_set("total_available_contacts",cont_total)
		camp_obj.save(ignore_permissions=True)

		if camp_obj.prospect_order == "Random":
			co=frappe.db.get_all("Call",filters={"campaign":"CAMP-2024-00009"},fields=["scheduled_queue"],order_by='scheduled_queue desc')
			queue=1
			if co:
				queue=int(co[0].get("scheduled_queue"))+1
			for row in camp_obj.contact_list:
				if not frappe.db.get_value("Call",{"contact":row.contact,"campaign":camp_obj.name},["name"]):
					agent_cnt = len(camp_obj.get('agents_list'))
					if row.call_done != 1:
						for agent in camp_obj.get('agents_list'):
							if agent.idx == agent_cnt_val:

								call = frappe.new_doc("Call")
								call.campaign = camp_obj.name
								call.contact = row.contact
								if camp_obj.agent_name:
									call.agents_name = agent.agent

								cc=frappe.get_doc("Campaign Contact",row.contact)
								call.call_phone=cc.phone
								call.mobile_phone=cc.mobile_phone
								call.corporate_phone=cc.corporate_phone
								call.organization_phone=cc.organization_contact
								call.organization = row.organization if row.organization else None
								call.call_allocation = camp_obj.dialing
								call.scheduled_queue = queue
								# call.survey = self.survey
								call.campaigns_name = camp_obj.campaigns_name
								# call.get_email_phone_number()
								call.insert(ignore_permissions=True)
								queue += 1
								break

						if agent_cnt_val == agent_cnt:
							agent_cnt_val = 1
						else:
							agent_cnt_val += 1

					
			camp_designer =frappe.get_doc("Campaigns Designer", self.campaigns_name)
			if camp_designer:
				end_days = camp_designer.days
				if camp_obj.start_on:
					time_format = frappe.db.get_single_value('System Settings','time_format')
					if time_format == "HH:mm:ss":
						dd =datetime.strptime(camp_obj.start_on, '%Y-%m-%d %H:%M:%S.%f')
						camp_obj.expected_end = (dd + timedelta(days=int(end_days))).date()
					else:
						dd = datetime.strptime(self.start_on, '%Y-%m-%d %H:%M:%S')
						camp_obj.expected_end = (dd + timedelta(days=int(end_days))).date()

			self.db_set('status', 'Running')
			for row in self.contact_list:
				row.call_done = 1
			# self.save(ignore_permissions = True)
			self.reload()
		else:
			set_queue(camp_obj)
		frappe.msgprint("Campaign Started.{0} calls have been scheduled.".format(len(camp_obj.get('contact_list'))))
		
		return diff 
	# except:
	# 	return 1

def set_queue(self):
	query = """select cc.contact,cc.organization,tc.last_quality_date as date from `tabCall Contact Child` cc 
				inner join `tabCampaign Contact` tc on cc.contact = tc.name
				where cc.parenttype ='Campaigns' and cc.call_done != 1"""
	if self.prospect_order == "Quality Fifo":
		query +=" and cc.parent ='{0}' order by date ASC".format(self.name)

	if self.prospect_order == "Quality Lifo":
		query +=" and cc.parent ='{0}' order by date DESC".format(self.name)

	if self.prospect_order == "Create Lifo":
		query +=" and cc.parent ='{0}' order by tc.creation desc".format(self.name)

	if self.prospect_order == "Create Fifo":
		query +=" and cc.parent ='{0}' order by tc.creation asc".format(self.name)


	contact = frappe.db.sql(query,as_dict=True)
	agent_cnt = len(self.get('agents_list'))
	agent_cnt_val = 1

	co=frappe.db.get_all("Call",filters={"campaign":"CAMP-2024-00009"},fields=["scheduled_queue"],order_by='scheduled_queue desc')
	queue=1
	if co:
		queue=int(co[0].get("scheduled_queue"))+1
	for cont in contact:
		if not frappe.db.get_value("Call",{"contact":cont.contact,"campaign":self.name},["name"]):
			for agent in self.get('agents_list'):
				if agent.idx == agent_cnt_val:
					call = frappe.new_doc("Call")
					call.campaign = self.name
					call.contact = cont.get('contact')
					call.organization = cont.get('organization') if cont.get('organization') else None
					call.call_allocation = self.dialing
					if self.agent_name:
						call.agents_name = agent.agent
					cc=frappe.get_doc("Campaign Contact",cont.get('contact'))
					call.call_phone=cc.phone
					call.mobile_phone=cc.mobile_phone
					call.corporate_phone=cc.corporate_phone
					call.organization_phone=cc.organization_contact
					call.scheduled_queue =queue
					# call.survey = self.survey
					call.campaigns_name = self.campaigns_name
					# call.get_email_phone_number()
					call.insert(ignore_permissions=True)
					queue +=1	
					break
			if agent_cnt_val == agent_cnt:
				agent_cnt_val = 1
			else:
				agent_cnt_val += 1

@frappe.whitelist()
def get_contact_list(filters, name, doc):
	try:
		new_email_list=[]
		self_doc = frappe.get_doc("Campaigns Designer", name)
		res = json.loads(filters) if filters else {}
		res['dnc'] = ['=', '0']
		res['wrong_number'] = ['=','0']
		
		for key in ["department", "title", "keywords"]:
			res.pop(key, None)

		resulted_contact = []
		allowed_contact = []
		organization_suppression = [row.domain for row in self_doc.company_suppression]
		abm_list = [row.domain for row in self_doc.abm_list]
		# Get excepted contacts by email
		if organization_suppression:
			excepted_contact_supp = frappe.get_all(
				"Campaign Contact",
				filters={'email': ['in', organization_suppression]},
				fields=['name']
			)
			resulted_contact.extend(e_cont.name for e_cont in excepted_contact_supp)

		if abm_list:
			org_list = frappe.get_all(
				"Campaign Organization",
				filters={'domain': ['in', abm_list]},
				fields=['name']
			)
			allowed_contact.extend(org.name for org in org_list)

		if resulted_contact:
			res['name'] = ['not in', resulted_contact]
		if allowed_contact:
			res['organization'] = ['in', allowed_contact]

		limit = self_doc.max_number_of_contacts if self_doc.max_number_of_contacts > 0 else None
		if doc:
			limit = doc.max_number_of_contacts
		contacts = frappe.get_all(
			"Campaign Contact", 
			filters=res, 
			fields=['name', 'organization', 'mobile_phone', 'phone', 'corporate_phone', 'email', 'organization_contact'],
			limit=limit
		)

		return_list = []
		for contact in contacts:
			new_email_list.append(contact.email)
			contact_dict = {
				'contact': contact.name,
				'organization': contact.organization,
				'mobile': contact.mobile_phone,
				'phone': contact.phone,
				'corporate_phone': contact.corporate_phone,
				'email': contact.email,
				'organization_contact': contact.organization_contact
			}
			return_list.append(contact_dict)
		
		total_available_contacts = len(return_list)
		return_list.append({'total_available_contacts': total_available_contacts})
		# self_doc.send_email(new_email_list)
		if not doc:
			enqueue(method=self_doc.send_email, queue='long', timeout=6000, new_email_list=new_email_list)

		return return_list

	except Exception as e:
		frappe.log_error(f"Error in get_contact_list: {str(e)}")
		return {'error': str(e)}
