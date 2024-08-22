# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CampaignLead(Document):
	# def get_email_phone_number(self):
	# 	phone_remove = []
	# 	email_remove = []
	# 	for s in self.get("phone_number"):
	# 		phone_remove.append(s)
	# 	for d in phone_remove:
	# 		self.remove(d)
	# 	for s in self.get("email"):
	# 		email_remove.append(s)
	# 	for d in email_remove:
	# 		self.remove(d)
	# 	agents = frappe.db.sql(
	# 		"""select phone,mobile_phone,corporate_phone from `tabCampaign Contact` where name = %s""",(self.contact))
	# 	for a in agents:
	# 		# print("-----phone------",a)
	# 		row = self.append("phone_number", {})
	# 		row.phone = a[0]
	# 		row.is_primary_phone = a[1]
	# 		row.is_primary_mobile_no = a[2]

	# 	emails = frappe.db.sql("""select email_id,is_primary from `tabContact Email` where parent = %s""",(self.contact))
	# 	for a in emails:
	# 		# print("-------email----", a)
	# 		row = self.append("email", {})
	# 		row.email_id = a[0]
	# 		row.is_primary = a[1]

	def on_submit(self):
		data =[]
						
		query = """select 
						TC.full_name as contact,
						TC.first_name,
						TC.last_name,
						TC.email,
						TC.phone,
						TC.seniority,
						TOrg.company_phone as organization_num,
						TOrg.name as organization_code,
						TOrg.address,
						TOrg.city,
						TOrg.state,
						TOrg.country,
						TOrg.postal_code as pincode,
						TOrg.employees,
						TOrg.industry as main_industry,
						TOrg.sub_industry,
						TOrg.website,
						TOrg.annual_revenue,
						TOrg.website as organization_link,
						TOrg.domain,
						TCL.name as Lead,
						TCL.call,
						TCMP.customer_name,
						TCMP.name as campaign
						from `tabCampaign Lead` TCL
						inner join `tabCampaigns` TCMP on TCMP.name = TCL.campaign 
						inner join `tabCampaign Contact` TC on TC.name = TCL.contact
						left join `tabCampaign Organization` TOrg on TC.organization =TOrg.name
						
						where TCL.name ='{0}'""".format(self.name)
		result = frappe.db.sql(query, as_dict=True)

		tlist_uc = []
		seniority = None
		title_query = frappe.db.sql("""select tt.title 
										from `tabCampaign Lead` as cl 
										join `tabCampaign Contact` as cc on cc.name = cl.contact 
										join `tabTitle Table` as tt on tt.parent = cc.name 
										where cl.name = "{0}"  """.format(self.name),as_list=True)


		
		
		
		
		for i in title_query:
			tlist_uc.append(i[0])

		
		
		


		for res in result:
			
			main_industry_id = None
			

			if res.get("organization_code") and res.get("main_industry"):
				main_industry = frappe.db.sql("""Select client_db_value from `tabCampaign Client Mapping` TCCM
												inner join `tabCampaigns Designer` TCD on TCD.name = TCCM.parent
												inner join `tabCampaigns` TCMP on TCD.name = TCMP.campaigns_name 
												where TCMP.name = %s and  TCCM.map_field ='Industry Type' and database_field =%s limit 1 """,
										 (res.get("campaign"), res.get("main_industry")))
				if main_industry:
					main_industry_id = main_industry[0][0]
			
			seniority_id = None
			if res.get("organization_code") and res.get("seniority"):
				seniority = frappe.db.sql("""Select client_db_value from `tabCampaign Client Mapping` TCCM
												inner join `tabCampaigns Designer` TCD on TCD.name = TCCM.parent
												inner join `tabCampaigns` TCMP on TCD.name = TCMP.campaigns_name 
												where TCMP.name = %s and  TCCM.map_field ='Seniority' and database_field =%s limit 1 """,
										 (res.get("campaign"), res.get("seniority")))
				if seniority:
					seniority_id = seniority[0][0]

			lr = frappe.new_doc("Lead Report")
			lr.first_name = res.get("first_name")
			lr.last_name = res.get("last_name")
			if title_query:
				ttl_id = None
				tlist = []
				for i in title_query:
					if res.get("organization_code") and i[0]:
						ttl = frappe.db.sql("""Select client_db_value from `tabCampaign Client Mapping` TCCM
														inner join `tabCampaigns Designer` TCD on TCD.name = TCCM.parent
														inner join `tabCampaigns` TCMP on TCD.name = TCMP.campaigns_name 
														where TCMP.name = %s and  TCCM.map_field ='Title' and database_field =%s limit 1 """,
												(res.get("campaign"), i[0]))
						if ttl:
							tlist_uc.append(ttl[0][0])
							tlist_uc.remove(i[0])
						else:
							tlist_uc.append(i[0])
				
				print("sjvnjsvjknvjjdnv j jdfjdjf jdf d d kd",tlist_uc)
					
				lr.title =   ','.join(tlist_uc)
				
			lr.seniority = seniority_id if seniority_id else res.get("seniority")
			lr.email = res.get("email")
			lr.organization = res.get("organization_code")
			lr.organization_num = res.get("organization_num")
			lr.address = res.get("address")
			lr.city = res.get("city")
			lr.state = res.get("state")
			lr.postal_code = res.get("pincode")
			lr.country = res.get("country")
			lr.employees =  res.get("employees")
			lr.sub_industry = res.get("sub_industry")
			lr.main_industry = res.get("main_industry")
			lr.website = res.get("website")
			lr.annual_revenue = res.get("annual_revenue")
			lr.organization_link = res.get("organization_link")
			lr.domain = res.get("domain")
			lr.lead = res.get("Lead")
			lr.customer = res.get("customer_name")
			lr.campaign = res.get("campaign")
			lr.call_id = res.get("call") if res.get("call") else None
			lr.insert(ignore_permissions=True)