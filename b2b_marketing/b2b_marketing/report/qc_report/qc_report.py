# Copyright (c) 2013, Dexciss and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import  getdate
from datetime import datetime

def execute(filters=None):
	columns = get_column(filters)
	data = get_data()
	return columns, data

def get_column(filters):
	columns = [
		{
			"label": _("Month"),
			"fieldname": "month",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Quality Date"),
			"fieldname": "quality_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Advisor Name"),
			"fieldname": "quality_done",
			"options": "Agents",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Campaign Name"),
			"fieldname": "campaign_name",
			"options": "Campaigns",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Call Type"),
			"fieldname": "call_type",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Team Leader"),
			"fieldname": "team_leader",
			"options": "Agents",
			"fieldtype": "Link",
			"width": 120
		},
		{
			"label": _("Manager Name"),
			"fieldname": "manager",
			"fieldtype": "Data",
			"width": 120
		}
	]

	rows = frappe.db.sql("""select DISTINCT(objective)from `tabQuality Review Objective`""",as_dict=True)
	if rows:
		for i in rows:
			columns.append(
				{
					"label": _(i.get('objective')),
					"fieldname": (i.get('objective')).lower().replace(" ", "_"),
					"fieldtype": "Data",
					"width": 120
				}
			)
			columns.append(
				{
					"label": _("Quality Rating"),
					"fieldname": "rating_" + (i.get('objective')).lower().replace(" ", "_"),
					"fieldtype": "Data",
					"width": 120
				}
			)
			columns.append(
				{
					"label": _("Quality Points"),
					"fieldname": "points_" + (i.get('objective')).lower().replace(" ", "_"),
					"fieldtype": "Data",
					"width": 120
				}
			)
			columns.append(
				{
					"label": _("Marks"),
					"fieldname": "marks_" + (i.get('objective')).lower().replace(" ", "_"),
					"fieldtype": "Int",
					"width": 120
				}
			)
			columns.append(
				{
					"label": _("Is Fatal"),
					"fieldname": "fatal_" + (i.get('objective')).lower().replace(" ", "_"),
					"fieldtype": "Check",
					"width": 120
				}
			)

	columns.append(
		{
			"label": _("Overall Comments"),
			"fieldname": "comment",
			"fieldtype": "Text",
			"width": 120
		}
	)
	columns.append(
		{
			"label": _("Overall Score"),
			"fieldname": "overall_score",
			"fieldtype": "Data",
			"width": 120
		}
	)
	columns.append(
		{
			"label": _("Overall Score without Fatal"),
			"fieldname": "overall_score_without_fatal",
			"fieldtype": "Float",
			"width": 120
		}
	)
	columns.append(
		{
			"label": _("Feedback Shared"),
			"fieldname": "feedback",
			"fieldtype": "Text",
			"width": 120
		}
	)
	columns.append(
		{
			"label": _("Additional Comments"),
			"fieldname": "additional_comment",
			"fieldtype": "Text",
			"width": 120
		}
	)
	columns.append(
		{
			"label": _("Area of Improvement 1"),
			"fieldname": "area_of_improvement_1",
			"fieldtype": "Text",
			"width": 120
		}
	)
	columns.append(
		{
			"label": _("Area of Improvement 2"),
			"fieldname": "area_of_improvement_2",
			"fieldtype": "Text",
			"width": 120
		}
	)
	columns.append(
		{
			"label": _("Area of Improvement 3"),
			"fieldname": "area_of_improvement_3",
			"fieldtype": "Text",
			"width": 120
		}
	)
	columns.append(
		{
			"label": _("Result"),
			"fieldname": "result",
			"fieldtype": "Data",
			"width": 120
		}
	)
	return columns

def get_data():
	data =[]
	query = frappe.db.sql("""select name from `tabQuality Review` where status = 'Closed'""", as_dict=True)
	month_dic = {1: 'January',2: 'February',3: 'March',4: 'April',5: 'May',6: 'June',7: 'July',8: 'August',9: 'September',10: 'October',11: 'November',12: 'December'}
	for res in query:
		campaign_name = None
		team_leader = None
		quality_done = None
		manager = None
		call_type = None

		q_review = frappe.get_doc("Quality Review",res.get("name"))
		if q_review:
			if q_review.quality_type == 'Call' and q_review.value:
				quality_done,team_leader,call_type,manager,campaign_name = get_agent_campiagn(q_review.value)

			if q_review.quality_type == 'Campaign Lead' and q_review.value:
				lead_id = frappe.get_doc("Campaign Lead", q_review.value)
				if lead_id and lead_id.call:
					quality_done,team_leader,call_type,manager,campaign_name = get_agent_campiagn(lead_id.call)

			row = {
				"month": month_dic[q_review.date.month],
				"quality_date": q_review.date,
				"comment": q_review.comment,
				"feedback": q_review.feedback,
				"additional_comment": q_review.additional_information,
				"area_of_improvement_1": q_review.area_of_improvement_1,
				"area_of_improvement_2": q_review.area_of_improvement_2,
				"area_of_improvement_3": q_review.area_of_improvement_3,
				"result": q_review.result,
				"campaign_name": campaign_name,
				"team_leader": team_leader,
				"quality_done": quality_done,
				"call_type": call_type,
				"manager": manager
				}
			fatal_list = []
			total = 0.0
			for s in q_review.reviews:
				rating = s.quality_rating
				if not rating:
					rating = 0
				if int(rating) > 3:
					row[s.objective.lower().replace(" ", "_")] = "Excellent"
				if int(rating) == 3:
					row[s.objective.lower().replace(" ", "_")] = "Average"
				if int(rating) < 3:
					row[s.objective.lower().replace(" ", "_")] = "Needs Improvement"
				row["rating_" + (s.objective.lower().replace(" ", "_"))] = rating
				row["points_" + (s.objective.lower().replace(" ", "_"))] = s.quality_points
				row["marks_" + (s.objective.lower().replace(" ", "_"))] = s.marks
				row["fatal_" + (s.objective.lower().replace(" ", "_"))] = s.is_fatal
				fatal_list.append(s.is_fatal)
				total += rating +s.marks
			if 1 in fatal_list:
				row["overall_score"] = 	"Fatal"
			else:
				row["overall_score"] = total
			row["overall_score_without_fatal"] = total
			data.append(row)
	return data

def get_agent_campiagn(doc_name):
	campaign_name = None
	team_leader = None
	quality_done = None
	manager = None
	call_type =None

	call_id = frappe.get_doc("Call",doc_name)
	if call_id:
		campaign_name = call_id.campaign
		call_type = call_id.call_disposal
		camp_des_name = frappe.db.sql("""select campaigns_name from `tabCampaigns` where name =%s limit 1""",(campaign_name))
		if camp_des_name:
			camp_desig = frappe.get_doc("Campaigns Designer", camp_des_name[0][0])
			if camp_desig:
				team_leader = camp_desig.agent_name

		res = frappe.db.sql("""select TA.name,TE.reports_to from `tabAgents` TA
								inner join `tabEmployee` TE on TA.employee = TE.name
								inner join `tabUser` TU on TU.name =TE.user_id
								inner join `tabCall` TC on TC.completed_by =TU.name
								where TC.name =%s limit 1""", (call_id.name), as_dict=True)
		for s in res:
			if s.get('name'):
				quality_done = s.get('name')
				if s.get('reports_to'):
					manager_name = frappe.get_doc("Employee",s.get('reports_to'))
					manager = manager_name.employee_name
	return quality_done,team_leader,call_type,manager,campaign_name

