# -*- coding: utf-8 -*-__newname
# Copyright (c) 2020, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import timeit
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import PHONE_NUMBER_PATTERN

class OrganizationCreationTool(Document):
	def get_eta(self, current, total, processing_time):
		self.last_eta = getattr(self, "last_eta", 0)
		remaining = total - current
		eta = processing_time * remaining
		if not self.last_eta or eta < self.last_eta:
			self.last_eta = eta
		return self.last_eta
	

	def on_submit(self):
		self.make_organization()

	@frappe.whitelist()
	def make_organization(self):
			org_names = []
			ct_names = []
			zf=[]
			if not self.company:
				frappe.throw(_("Please select the Company"))

			start = timeit.default_timer()
			processing_time = timeit.default_timer() - start
			
			for row in self.organizations:
				eta = self.get_eta(row.idx, len(self.organizations), processing_time)
				frappe.publish_realtime(
						"data_import_progress",
						{
							"current": row.idx,
							"total": len(self.organizations),
							"skipping": True,
							"data_import": self.name,
							"success": True,
							"eta":eta
						},
						user=frappe.session.user,
					)
				
				value=0
				try:
					if row.phone:
						row.phone=sanitize_phone(row.phone,row.idx)
						if validate_phone(row.phone):
							value+=1
					else:
						value+=1
					if row.mobile_phone:
						row.mobile_phone=sanitize_phone(row.mobile_phone,row.idx)
						if validate_phone(row.mobile_phone):
							value+=1
					else:
						value+=1
					if row.company_phone:
						row.company_phone=sanitize_phone(row.company_phone,row.idx)
						if validate_phone(row.company_phone):
							value+=1
					else:
						value+=1
					if row.corporate_phone:
						row.corporate_phone=sanitize_phone(row.corporate_phone,row.idx)
						if validate_phone(row.corporate_phone):
							value+=1
					else:
						value+=1

					if value==4:
						if row.email_verified:
							if row.email_verified=="Verified":
								row.email_verified="Verified"
							else:
								row.email_verified="Unavailable"

						if row.org_country:
							if not frappe.db.exists("Country",row.org_country):
								doc=frappe.new_doc("Country")
								doc.country_name=row.org_country
								doc.save(ignore_permissions=True)
						
						if row.contact_country:
							if not frappe.db.exists("Country",row.contact_country):
								doc=frappe.new_doc("Country")
								doc.country_name=row.contact_country
								doc.save(ignore_permissions=True)

						if row.industry:
							if not frappe.db.exists("Industry Type",row.industry):
								if self.missing_main_industry:
									self.add_main_industry(row.industry)
								else:
									frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("Main Industry"), frappe.bold(row.industry)))

						if row.sub_industry:
							if not frappe.db.exists("Sub Industry Type",row.sub_industry):
								if self.missing_sub_industry:
									self.add_sub_industry(row.sub_industry)
								else:
									frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("Sub Industry"), frappe.bold(row.sub_industry)))

						

						if row.seniority:
							if not frappe.db.exists("Seniority",row.seniority):
								if self.create_missing_seniority:
									self.add_seniority(row.seniority)
								else:
									frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("Seniority"), frappe.bold(row.seniority)))
						kw = []
						ukw = []
						if row.keywords:
							
							if "," in row.keywords:
								kw = list(row.keywords.split(","))
							
								if kw:
									# print("keywords",ukw)
									for keyword in kw:
										keyword = keyword.lstrip()
										keyword = keyword.rstrip()
										if not frappe.db.exists("Tag",keyword):
											if self.create_missing_keywords:
												self.add_keywords(keyword)
												# print("***************keywmiss **********************")
											else:
												frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("Keywords"), frappe.bold(keyword)))
							else:
								if not frappe.db.exists("Tag",row.keywords):
									if self.create_missing_keywords:
										self.add_keywords(row.keywords)
										kw.append(row.keywords)
										# print("***************keywords appended**********************")
									else:
										frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("Keywords"), frappe.bold(row.keywords)))
							# print("kw list after spaces removal",kw)
						sc = []
						if row.sic_codes:
							if "," in row.sic_codes:
								# print("***************In  sis code**********************")
								sc = list(row.sic_codes.split(","))
								
								if sc:
									for sic_code in sc:
										sic_code = sic_code.lstrip()
										sic_code = sic_code.rstrip()
										if not frappe.db.exists("SIC Codes",sic_code):
											# print("***************SIC CODE not exist in db**********************")
											if self.create_missing_sic_codes:
												self.add_sic_codes(sic_code)
											else:
												frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("SIC Codes"), frappe.bold(row.sic_codes)))
							else:
								if not frappe.db.exists("SIC Codes",row.sic_codes):
									# print("***************keywords without comma seperated**********************")
									if self.create_missing_sic_codes:
										self.add_sic_codes(row.sic_codes)
										sc.append(row.sic_codes)
									else:
										frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("SIC Codes"), frappe.bold(row.sic_codes)))
								else:
									sc.append(row.sic_codes)

						if row.org_name:
							if not frappe.db.exists("Campaign Organization",{'or_name':row.org_name}) or not frappe.db.exists("Campaign Organization",{'website':row.website}):
								# print("***************Org_name* not in db*********************",row.org_name)
								org = frappe.new_doc("Campaign Organization")
								org.or_name = row.org_name
								org.employees = row.employees
								org.linkedin_url = row.linkedin_url
								org.website = row.website
								org.fb_url = row.fb_url
								org.twitter_url = row.twitter_url
								org.annual_revenue = row.annual_revenue
								org.revenue_currency = row.revenue_currency
								org.founded_year = row.founded_year
								org.industry = row.industry
								org.sub_industry = row.sub_industry
								org.domain = row.domain
								if kw:
									for i in kw:
										i = i.lstrip()
										i = i.rstrip()
										org.append("keywords",{
											"keywords":i
										})
										# print("i in make organization",i)

								if sc:
									for j in sc:
										j = j.lstrip()
										j = j.rstrip()
										org.append("sic_codes",{
											"sic_code":j
										})
								org.seo_description = row.seo_description
								org.address = row.address
								org.city = row.org_city
								org.state = row.org_state
								org.country = row.org_country
								org.postal_code = row.postal_code
								org.company_phone = row.company_phone

								
								org.insert(ignore_permissions=True)
								print("gggggggggorg name dddddddddddddd",org_names)
								if org.name not in org_names:
									# print("***********************************************************if")
									org_names.append(org.name)
								add_ref = ""
								if row.first_name and row.last_name:
									# print("###########################$$$$$$$$$$$$$$$$$$$$$$")
									ct = self.make_contact(row, org)
									if ct:
										ct_names.append(ct)  
							else:
								if row.org_name not in zf:
									zf.append(row.org_name)
								org = frappe.get_doc('Campaign Organization',{'or_name':row.org_name})
								if org.name:
									if row.first_name and row.last_name:
										ct = self.make_contact(row, org)
										if ct:
											ct_names.append(ct)


					else:
						frappe.log_error(title = 'Organization Campaign/Contact Creation Error',message="row"+str(row.idx)+"/n"+ str("Phone No Is Invalid"))
						


								
				except:	
					traceback = frappe.get_traceback()
					frappe.log_error(title = 'Organization/Campaign Contact Creation Error',message="row"+str(row.idx)+"/n"+ str(traceback))
					
	        
			# print("names of organization",org_names,len(org_names))
			# print("names of ct",ct_names,len(ct_names))
			# self.campaign_organization_count=len(org_names)
			# self.campaign_contact_count=len(ct_names)
			frappe.db.set_value("Organization Creation Tool", {"name":self.name}, {
						"campaign_organization_count": len(org_names),
						"campaign_contact_count": len(ct_names)
					})
			print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy************************************",len(org_names))
			print("*****************************************************************************",len(ct_names))
			if org_names and ct_names:
				if len(org_names) <(len(self.organizations)-len(zf)):
					self.db_set("status","Partially Success")
					doc_link = '<a href="/app/error-log">{0}</a>'.format(len(org_names))
					frappe.msgprint("Organization creation tool has run successfully, and has created {0} Organizations, {1} Contacts. There were  {2} errors and {3} Duplicate Organization Present.".format(len(org_names),len(ct_names),doc_link,len(zf)))
				else:
					self.db_set("status","Success")
					frappe.msgprint("Organization creation tool has run successfully, and has created {0} Organizations, {1} Contacts and {2} Duplicate Organization Present.".format(len(org_names),len(ct_names),len(zf)))

			else:
				frappe.msgprint("Organizations Already Exist Or Error Already Present")

			if len(org_names)==0:
				self.db_set("status","Failed")



			
		
	def make_contact(self, row, organization1):
     
		# try:
			clist=[]
			if not frappe.db.get_value("Campaign Contact",{"email":row.email},["name"]):
				
				contact = frappe.new_doc("Campaign Contact")
				contact.first_name = row.first_name
				contact.last_name = row.last_name
				contact.full_name =  "{0} {1}".format(row.first_name,row.last_name) if row.last_name else "{0}".format(row.first_name)
				contact.organization = organization1.name
				contact.email = row.email
				contact.email_verified = row.email_verified
				contact.additional_email = row.additional_email
				contact.seniority = row.seniority
				contact.facebook_url = row.ct_fb
				contact.phone = row.phone
				contact.mobile_phone = row.mobile_phone
				contact.corporate_phone = row.corporate_phone
				contact.linkedin_url = row.ct_linkedin
				contact.twitter_url = row.ct_twitter
				contact.city = row.contact_city
				contact.state = row.contact_state
				contact.country = row.contact_country
				og = frappe.get_doc("Campaign Organization",organization1.name)
				contact.keywords = og.keywords
				
				contact.dnc = row.dnc
				

				kw = []
				if row.department:
					if "," in row.department:
						kw = list(row.department.split(","))
						
						if kw:
							for keyword in kw:
								keyword = keyword.lstrip()
								keyword = keyword.rstrip()
								if not frappe.db.exists("Campaign Department",keyword):
									if self.missing_department:
										self.add_department(keyword)
									else:
										frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("Campaign Department"), frappe.bold(keyword)))
					else:
						if not frappe.db.exists("Campaign Department",row.department):
							if self.missing_department:
								self.add_department(row.department)
								kw.append(row.department)
							else:
								frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("Campaign Department"), frappe.bold(row.department)))

						else:
							kw.append(row.department)
				if kw:
					for dpt in kw:
						dpt = dpt.lstrip()
						dpt = dpt.rstrip()
						contact.append("department",{
							"department":dpt

						})

				ttl = []
				if row.title:
					if "," in row.title:
						ttl = list(row.title.split(","))
						
						if ttl:
							for title in ttl:
								title = title.lstrip()
								title = title.rstrip()
								if not frappe.db.exists("Title",title):
									if self.create_missing_title:
										self.add_title(title)
									else:
										frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("Title"), frappe.bold(title)))
					else:
						if not frappe.db.exists("Title",row.title):
							if self.create_missing_title:
								self.add_title(row.title)
								ttl.append(row.title)
							else:
								frappe.throw(_("Row {0}: {1} {2} does not exist.").format(row.idx,frappe.bold("Title"), frappe.bold(row.title)))
						else:
							ttl.append(row.title)


				if ttl:
					for t in ttl:
						t = t.lstrip()
						t = t.rstrip()
						contact.append("title",{
							"title":t

						})
				



				contact.save(ignore_permissions=True)
				return contact.name

		

	def add_main_industry(self,main_industry):
		industry = frappe.new_doc("Industry Type")
		industry.industry = main_industry
		industry.insert(ignore_permissions=True)

	def add_sub_industry(self,sub_industry):
		industry = frappe.new_doc("Sub Industry Type")
		industry.sub_industry = sub_industry
		industry.insert(ignore_permissions=True)

	
	def add_department(self,department):
		dept = frappe.new_doc("Campaign Department")
		dept.department_name = department
		dept.insert(ignore_permissions=True)


	def add_title(self,title):
		if title:
			tle=frappe.db.get_value("Title",{"title":title},"name")
			if not tle:
				tt = frappe.new_doc("Title")
				tt.title = title
				tt.insert(ignore_permissions=True)
	
	def add_keywords(self,keywords):
		if keywords:
			if not frappe.db.exists("Tag",keywords):
				k = frappe.new_doc("Tag")
				k.name = keywords
				k.save(ignore_permissions = True)

	def add_sic_codes(self,sic_codes):
		if sic_codes:
			k = frappe.new_doc("SIC Codes")
			k.sic_code = sic_codes
			k.save(ignore_permissions = True)

		
	
	def add_seniority(self,seniority):
		snr = frappe.new_doc("Seniority")
		snr.name1 = seniority
		snr.insert(ignore_permissions=True)
	


	def address_query(self,links):
		# print("links------------------",links)
		import json

		links = [{"link_doctype": d.get("link_doctype"), "link_name": d.get("link_name")} for d in links]
		result = []

		for link in links:
			if not frappe.has_permission(doctype=link.get("link_doctype"), ptype="read", doc=link.get("link_name")):
				continue

			res = frappe.db.sql("""
				SELECT `tabAddress`.name
				FROM `tabAddress`, `tabDynamic Link`
				WHERE `tabDynamic Link`.parenttype='Address'
					AND `tabDynamic Link`.parent=`tabAddress`.name
					AND `tabDynamic Link`.link_doctype = %(link_doctype)s
					AND `tabDynamic Link`.link_name = %(link_name)s
			""", {
				"link_doctype": link.get("link_doctype"),
				"link_name": link.get("link_name"),
			}, as_dict=True)

			result.extend([l.name for l in res])

		return result

	@frappe.whitelist()
	def select_check(self):
		self.missing_main_industry=1
		self.missing_sub_industry=1
		self.create_missing_seniority=1
		self.create_missing_keywords=1
		self.missing_department=1
		self.create_missing_title=1
		self.create_missing_sic_codes=1
		self.create_missing_country=1
  
@frappe.whitelist()
def sanitize_phone(phone=None,idx=None):
	string=""
	if phone:
		if "." in str(phone):
			string=str(phone).replace(".","")
		if "-" in str(phone):
			string=str(phone).replace("-","")
		if "(" in str(phone):
			string=str(phone).replace("(","")
		if ")" in str(phone):
			string=str(phone).replace(")","")
		if "`" in str(phone):
			string=str(phone).replace("`","")
		if " " in str(phone):
			string=str(phone).replace("  ","")
		if "'" in str(phone):
			string=str(phone).replace("'","")

	
	return string



def validate_phone(phone):
	# phone_number = phone.strip()
	# print("##########################",phone)
	match = PHONE_NUMBER_PATTERN.match(phone)
	# print("#################################match",match)
	return bool(match)