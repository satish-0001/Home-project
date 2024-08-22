# Copyright (c) 2021, Dexciss and contributors
# For license information, please see license.txt

from datetime import datetime
import frappe
from frappe import permissions
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, get_link_to_form, nowtime
from frappe.utils import now_datetime, nowdate
import pytz

from frappe.utils.data import get_time

class CallCampaign(Document):
	@frappe.whitelist()
	def get_options(self, arg=None):
		if self.get("contact"):
			doc = frappe.get_doc("Campaign Contact", self.get("contact"))
			lst = []
			st = ""
			lst.append(str(doc.phone)+ " " +"(Phone)")
			lst.append(str(doc.mobile_phone)+ " " +"(Mobile Phone)")
			lst.append(str(doc.corporate_phone)+ " " +"(Corporate Phone)")
			for number in lst:
				st += str(number) + '\n'
			return st
	
	@frappe.whitelist()
	def check_scheduled_call(self):
		self.start_campaign_call_list = []
		agent_available_calls = frappe.db.get_all("Call", filters={'campaign':self.campaign,'agents_name': self.agent, 'status': "Scheduled"}, fields=['name'], order_by="scheduled_queue")
		if not agent_available_calls:
			frappe.msgprint("No Scheduled calls for the selected campaing. Please select another campaign or contact your manager")
			exist = True
			return exist
	
	@frappe.whitelist()
	def get_call(self):
		self.start_campaign_call_list = []
		agent_available_calls = frappe.db.get_all("Call", filters={'campaign':self.campaign,'agents_name': self.agent, 'status': "Scheduled"}, fields=['name'], order_by="scheduled_queue")
		if not agent_available_calls:
			return True
		call_list = []
		for data in agent_available_calls:
			if data.name:
				call_list.append(data.name)
			
		return call_list
	
	@frappe.whitelist()
	def get_call_self(self,call):
		call = frappe.get_doc("Call",call)
		if call.contact:
			contact=frappe.get_doc("Campaign Contact",call.contact)
			if contact.timezone:
				timezone = pytz.timezone(contact.timezone)
				prefered_time=frappe.db.get_value("Country Multiselect",{"country":call.country},"parent")
				if prefered_time:
					current_time = datetime.now(timezone)
					current_day = current_time.strftime('%A')
					pts=frappe.get_doc("Preferred Call Time",prefered_time)
					for k in pts.preferred_call_time_slots:
						if k.day==current_day:
							current_time_str = current_time.strftime('%H:%M:%S')
							if get_time(k.from_time) <=get_time(current_time_str) and get_time(k.to_time)>=get_time(current_time_str):
								return True
			else:
				return True



					


	@frappe.whitelist()
	def change_status_complete_p(self):
		call_obj = frappe.get_doc("Call",self.call)
		call_obj.status = "Completed"
		call_obj.end_time_ = now_datetime()
		call_obj.completed_by = frappe.session.user
		call_obj.save(ignore_permissions=True)
	@frappe.whitelist()
	def change_status_start(self):
		call_obj = frappe.get_doc("Call", self.call)
		call_obj.status = "On-going"
		call_obj.start_time_ = now_datetime()
		call_obj.save()
	@frappe.whitelist()
	def update_agent_status(self):
		agent = frappe.get_doc("Agents", self.agent)
		if agent.total_calls:
			agent.total_calls = int(agent.total_calls) + 1
		else:
			agent.total_calls = 1
		agent.db_update()
@frappe.whitelist()
def create_agent_log(agent,status,campaign,notes=None):
	from frappe.utils import add_days, getdate, now_datetime
	doc = frappe.new_doc("Agent Log")
	doc.agents = agent
	doc.datetime = now_datetime()
	doc.status = status
	doc.campaign = campaign
	doc.notes = notes if notes else ""
	doc.save(ignore_permissions=True)

@frappe.whitelist()
def filtered_campaigns(agent):
	print("trigger dshjdhjdfhjd")
	filtered_camps = []
	cam = frappe.db.get_all("Campaign Agent Child",{'agent':agent,"parenttype":"Campaigns"},['*'])
	print("hdhdjbdbhjdhdhbdj",cam)
	if cam:
		for data in cam:
			camps = frappe.db.get_value("Campaigns",{'name':data.parent,'status':"Running"},['name'])
			if camps:
				filtered_camps.append(camps)
		if filtered_camps:
			return filtered_camps
		else:
			frappe.msgprint("No Running Campaigns Found for Agent - {0}".format(agent))
				
