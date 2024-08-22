# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "b2b_marketing"
app_title = "B2B Marketing"
app_publisher = "Dexciss"
app_description = "markting"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "dexciss@info.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/b2b_marketing/css/b2b_marketing.css"
# app_include_js = "/assets/b2b_marketing/js/b2b_marketing.js"

# include js, css files in header of web template
# web_include_css = "/assets/b2b_marketing/css/b2b_marketing.css"
# web_include_js = "/assets/b2b_marketing/js/utils/organization_quick_entry.js"
# app_include_js = "assets/js/organization.min.js"
# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Quality Review" : "public/js/quality_review.js",
			  "Contact" : "public/js/contact.js",
			  "Sales Invoice" : "public/js/sales_invoice.js",
			 }

# treeviews = ['Agents']
doctype_list_js = {"Contact" : "public/js/contact_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "b2b_marketing.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "b2b_marketing.install.before_install"
# after_install = "b2b_marketing.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "b2b_marketing.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "Revenue Size": {
	# 	"validate": "b2b_marketing.b2b_marketing.doctype.revenue_size.revenue_size.size_validation"
	# },
	# "Employee Size": {
	# 	"validate": "b2b_marketing.b2b_marketing.doctype.employee_size.employee_size.size_validation"
	# },
	# "Quality Review": {
		# "validate": "b2b_marketing.b2b_marketing.doctype.call.call.set_submittable_property",
		# "on_submit": "b2b_marketing.b2b_marketing.doctype.call.call.set_quality_rating",
		# "on_cancel": "b2b_marketing.b2b_marketing.doctype.call.call.cancel_quality_rating",
	# },
# 	"Sales Invoice":{
# 		"after_insert": "b2b_marketing.b2b_marketing.doctype.invoice_build_up.invoice_build_up.change_invoice_build_up_status"
# 	},
# 	"Contact":{
# 		"after_insert": "b2b_marketing.b2b_marketing.doctype.organization.organization.set_organization_in_contact"
# 	},
# 	"Address":{
# 		"after_insert": "b2b_marketing.b2b_marketing.doctype.organization.organization.set_organization_in_address"
# 	}
}
# Scheduled Tasks
# ---------------
fixtures = [{
  'doctype': 'Custom Field',
  'filters': {
  'name': ['in', ('Quality Review-middle_name','Quality Review-email_id','Quality Review-custom_mobile_no','Quality Review-custom_job_position','Quality Review-custom_department','Quality Review-custom_job_function')]
   }
}]

scheduler_events = {
	"daily": [
		"b2b_marketing.b2b_marketing.scheduler_events.auto_change_campaign_status",
		"b2b_marketing.b2b_marketing.scheduler_events.reset_daily_limit_reach",
		"b2b_marketing.b2b_marketing.scheduler_events.daily_invoice_build",
		"b2b_marketing.b2b_marketing.scheduler_events.daily_get_contact_list_update"
	],
	"weekly": [
		"b2b_marketing.b2b_marketing.scheduler_events.weekly_invoice_build"
	],
	"monthly":[
		"b2b_marketing.b2b_marketing.scheduler_events.monthly_invoice_build"
	]
}

# Testing
# -------

# before_tests = "b2b_marketing.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "b2b_marketing.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "b2b_marketing.task.get_dashboard_data"
# }

override_doctype_class = {
    'Terms and Conditions':'b2b_marketing.b2b_marketing.terms_and_conditions.CustomTermsandConditions'
}