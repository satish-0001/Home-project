# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime
from datetime import timedelta

class Campaigns(Document):
	@frappe.whitelist()
	def set_sub_agents(self):
		to_remove = []
		for s in self.get("agents_list"):
			to_remove.append(s)
		for d in to_remove:
			self.remove(d)
		agents = frappe.db.sql("""select agents_name from `tabAgents` where parent_agents = %s""", (self.agent_name))
		for a in agents:
			row = self.append("agents_list", {})
			row.agent = a[0]
		self.get_online_agent_count()

	@frappe.whitelist()
	def get_online_agent_count(self):
		agent_list =[]
		for a in self.get("agents_list"):
			agent_list.append(a.agent)
		if agent_list:
			if len(agent_list) > 1:
				query ="""select name from `tabAgents` where status = 'Online'and name in {0}""".format(tuple(agent_list))
			else:
				query = """select name from `tabAgents` where status = 'Online'and name = '{0}'""".format(agent_list[0])
			online_agent = frappe.db.sql(query)
			self.online_agents = len(online_agent)
			self.number_of_agents = len(agent_list)
		else:
			self.number_of_agents = 0

	@frappe.whitelist()
	def get_callable_contact_count(self):
		if self.get("contact_list"):
			contact_list = 0
			for contact in self.contact_list:
				if not contact.phone and not contact.corporate_phone and not contact.mobile and not contact.organization_contact:
					contact_list += 1
			total_contacts = len(self.get("contact_list"))
			collable_contatcts = total_contacts - contact_list
			self.callable_contact=collable_contatcts
				

	@frappe.whitelist()
	def cancel_call_scheduled(self):
		scheduled_call_doc = frappe.db.get_all("Call",{"campaign":self.name,"status":'Scheduled'},['name'])
		for call in scheduled_call_doc:
			call_doc = frappe.get_doc("Call",call)
			call_doc.db_set("status","Cancelled")
		self.db_set("status","Cancelled")
		self.save()
	def onload(self):
		self.load_dashboard_info()

	def load_dashboard_info(self):						#show dashoabrad data
		info = {}
		count = frappe.db.sql("""select count(name) from `tabCampaign Lead` where campaign = %s""", (self.name))
		info["lead"] = float(count[0][0])
		rate = 0.0
		shortfall = 0.0
		if self.get("delivery_target"):
			if float(self.get("delivery_target")) > 0:
				rate = round(((float(count[0][0]) / float(self.get("delivery_target"))) * 100),2)
				shortfall = round((float(self.get("delivery_target")) - float(count[0][0])),2)
		info["rate"] = rate
		info["shortfall"] = shortfall
		self.set_onload('dashboard_info', info)

	@frappe.whitelist()
	def create_calls(self):
		if self.get('contact_list'):
			if self.prospect_order == "Random":
				queue = 1
				agent_cnt = len(self.get('agents_list'))
				agent_cnt_val = 1
				for a in self.get('contact_list'):
					if a.call_done != 1:
						for agent in self.get('agents_list'):
							if agent.idx == agent_cnt_val:
								call = frappe.new_doc("Call")
								call.campaign = self.name
								cc=frappe.get_doc("Campaign Contact",a.contact)
								call.call_phone=cc.phone
								call.mobile_phone=cc.mobile_phone
								call.corporate_phone=cc.corporate_phone
								call.organization_contact=cc.organization_contact
								call.contact = a.contact
								if self.agent_name:
									call.agents_name = agent.agent
								call.title = cc.title
								call.department = cc.department
								call.organization = a.organization if a.organization else None
								call.call_allocation = self.dialing
								call.scheduled_queue = queue
								call.campaigns_name = self.campaigns_name
								call.campaigns_exp_start=self.expected_start
								call.campaigns_exp_end=self.expected_end
								call.insert(ignore_permissions=True)
								queue += 1
								break
						if agent_cnt_val == agent_cnt:
							agent_cnt_val = 1
						else:
							agent_cnt_val += 1
			else:
				self.set_queue()
			frappe.msgprint("Campaign Started.{0} calls have been scheduled.".format(len(self.get('contact_list'))))

		camp_designer =frappe.get_doc("Campaigns Designer", self.campaigns_name)
		if camp_designer:
			end_days = camp_designer.days
			if self.start_on:
				time_format = frappe.db.get_single_value('System Settings','time_format')
				if time_format == "HH:mm:ss":
					dd =datetime.strptime(self.start_on, '%Y-%m-%d %H:%M:%S.%f')
					self.expected_end = (dd + timedelta(days=int(end_days))).date()
				else:
					dd = datetime.strptime(self.start_on, '%Y-%m-%d %H:%M:%S')
					self.expected_end = (dd + timedelta(days=int(end_days))).date()

		self.db_set('status', 'Running')
		for row in self.contact_list:
			row.call_done = 1
		self.reload()

	def set_queue(self):
		queue = 1
		contacts = frappe.get_all("Call Contact Child", 
								filters={"parenttype": "Campaigns",
										"call_done": 0,
										"parent": self.name},
								fields=["contact", "organization"],
								order_by="modified ASC" if self.prospect_order == "Quality Fifo" else
										"modified DESC" if self.prospect_order == "Quality Lifo" else
										"creation DESC" if self.prospect_order == "Create Lifo" else
										"creation ASC")

		agents_list = self.get('agents_list')
		agent_count = len(agents_list)
		agent_index = 0

		calls_to_insert = []
		for cont in contacts:
			agent = agents_list[agent_index]
			agent_index = (agent_index + 1) % agent_count

			call = frappe.new_doc("Call")
			call.campaign = self.name
			call.contact = cont.get('contact')
			call.organization = cont.get('organization') or None
			call.call_allocation = self.dialing
			if self.agent_name:
				call.agents_name = agent.agent

			cc = frappe.get_doc("Campaign Contact", cont.get('contact'))
			call.phone = cc.phone
			call.title = cc.title
			call.department = cc.department
			call.mobile_phone = cc.mobile_phone
			call.corporate_phone = cc.corporate_phone
			call.organization_phone = cc.organization_contact
			call.scheduled_queue = queue
			call.campaigns_name = self.campaigns_name
			call.campaigns_exp_start=self.expected_start
			call.campaigns_exp_end=self.expected_end
			# calls_to_insert.append(call)
			call.insert(ignore_permissions=True)
			queue += 1

		# Bulk insert calls
		# frappe.db.insert_many(calls_to_insert, ignore_permissions=True)

@frappe.whitelist()
def build_invoice(doc_name =None):
	query = frappe.db.sql("""select tcd.name as designer_name,
							 tc.name as campaign,
							 tcd.customer_name,
							 tcd.agent_name,
							 tcd.invoice_policy,
							 tcd.invoicing_frequency,
							 tcd.lead_call_fixed_price,
							 tcd.cost_center from `tabCampaigns Designer` as tcd 
							 inner join `tabCampaigns` as tc on tc.campaigns_name = tcd.name 
							 where tcd.invoice_policy ='Fixed Charge' and tcd.invoicing_frequency ='Campaign Complete'
							 and tc.name =%s""",(doc_name),as_dict=True)

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





