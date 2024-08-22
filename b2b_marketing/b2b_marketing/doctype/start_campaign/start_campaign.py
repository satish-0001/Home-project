# Copyright (c) 2021, Dexciss and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StartCampaign(Document):
	@frappe.whitelist()
	def get_call(self):
		self.start_campaign_call_list = []
		agent_available_calls = frappe.db.get_all("Call", filters={'agents_name':self.agent,'status':"Scheduled"}
												  ,fields=['phone'], order_by="scheduled_queue")
		call_list = []
		for data in agent_available_calls:
			print("data----------------------",data)
			if data.phone:
				# row = self.append("start_campaign_call_list", {})
				# row.call = data.phone
				call_list.append(data.phone)
		return call_list
