import frappe
from frappe.utils.data import getdate
from datetime import timedelta

def execute(filters=None):
    columns = col(filters)
    data = get_data(filters)
    chart = get_chart(data, filters)
    return columns, data, None, chart

def col(filters):
    columns = []

    if filters.get("based_on") == "Agent":
        columns.append({
            "label": "Agent",
            "fieldname": "agents_name",
            "fieldtype": "Link",
            "options": "Agents",
            "width": 200
        })
        columns.append({
            "label": "Supervisor %",
            "fieldname": "parent",
            "fieldtype": "Link",
            "options": "Agents",
            "width": 200
        })

    elif filters.get("based_on") == "Campaign":
        columns.append({
            "label": "Campaign",
            "fieldname": "campaign",
            "fieldtype": "Link",
            "options": "Campaigns",
            "width": 200
        })
        columns.append({
            "label": "Supervisor %",
            "fieldname": "parent",
            "fieldtype": "Link",
            "options": "Agents",
            "width": 200
        })

    elif filters.get("based_on") == "Supervisor":
        columns.append({
            "label": "Supervisor %",
            "fieldname": "parent",
            "fieldtype": "Link",
            "options": "Agents",
            "width": 200
        })

    elif filters.get("based_on") == "Customer":
        columns.append({
            "label": "Customer Name",
            "fieldname": "customer_name",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 200
        })

    common_columns = [
        {
            "label": "All Calls",
            "fieldname": "all_calls",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Completed Calls",
            "fieldname": "completed_calls",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Call Backs Requested",
            "fieldname": "call_backs_requested",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Answering Machine",
            "fieldname": "answering_machine",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Hang-up",
            "fieldname": "hang_up",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Successful Calls",
            "fieldname": "successful_calls",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Not Interested",
            "fieldname": "not_interested",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "DNC",
            "fieldname": "dnc_check_box",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Total Duration",
            "fieldname": "time_duration",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Scheduled Calls",
            "fieldname": "scheduled_calls",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Unanswered Calls",
            "fieldname": "unanswered_calls",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Other",
            "fieldname": "other",
            "fieldtype": "Data",
            "width": 200
        }
    ]
    columns.extend(common_columns)
    return columns

def condition(filters):
    conditions = []
    filter_values = {}
    
    if filters.get("campaign"):
        conditions.append("c.campaign IN %(campaign)s")
        filter_values["campaign"] = tuple(filters.get("campaign"))
        
    if filters.get("supervisor"):
        conditions.append("c.agents_name IN (SELECT name FROM `tabAgents` WHERE parent_agents IN %(supervisor)s)")
        filter_values["supervisor"] = tuple(filters.get("supervisor"))
        
    if filters.get("agent"):
        conditions.append("c.agents_name IN %(agent)s")
        filter_values["agent"] = tuple(filters.get("agent"))

    if filters.get("from_date") and filters.get("to_date"):
        from_date = filters.get("from_date")
        to_date = filters.get("to_date")
        conditions.append("(ca.expected_start >= %(from_date)s AND ca.expected_end <= %(to_date)s)")
        filter_values["from_date"] = from_date
        filter_values["to_date"] = to_date

    if filters.get("customer"):
        customer_filter = filters.get("customer")
        conditions.append("c.customer_name = %(customer)s")
        filter_values["customer"] = customer_filter

    if filters.get("company"):
        company = filters.get("company")
        conditions.append("ca.company = %(company)s")
        filter_values["company"] = company

    if not conditions:
        return "1=1", filter_values
    
    return " AND ".join(conditions), filter_values

def get_data(filters=None):
    data = []
    conditions, filter_values = condition(filters)
    
    if filters.get("based_on") == "Agent":
        query = frappe.db.sql(f"""
            SELECT 
                c.agents_name,
                c.campaign,
                ca.name,
                a.parent_agents AS parent,
                ca.company,
                COUNT(*) AS all_calls,
                SUM(CASE WHEN c.status = 'Completed' AND c.call_disposal = 'Lead Created' THEN 1 ELSE 0 END) AS successful_calls,
                SUM(CASE WHEN c.status = 'No-Answer' AND c.call_disposal = 'No Answer' THEN 1 ELSE 0 END) AS unanswered_calls,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Hang up' THEN 1 ELSE 0 END) AS hang_up,
                SUM(CASE WHEN c.status = 'Completed' THEN 1 ELSE 0 END) AS completed_calls,
                SUM(CASE WHEN c.status = 'Cancelled' AND c.is_daily_limit_reach = 1 THEN 1 ELSE 0 END) AS other,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Call Back' THEN 1 ELSE 0 END) AS call_backs_requested,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Answering Machine -' THEN 1 ELSE 0 END) AS answering_machine,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Not Interested' THEN 1 ELSE 0 END) AS not_interested,
                SUM(CASE WHEN c.status IS NOT NULL THEN TIMESTAMPDIFF(SECOND, c.start_time_, c.end_time_) ELSE 0 END) AS time_duration,
                SUM(CASE WHEN c.status IS NOT NULL AND p.dnc = 1 THEN 1 ELSE 0 END) AS dnc_check_box,
                SUM(CASE WHEN c.status = 'Scheduled' THEN 1 ELSE 0 END) AS scheduled_calls
            FROM `tabCall` AS c
            LEFT JOIN `tabAgents` AS a ON c.agents_name = a.name
            LEFT JOIN `tabCampaign Contact` AS p ON c.contact = p.name
            LEFT JOIN `tabCampaigns` AS ca ON ca.name = c.campaign
            WHERE {conditions}
            GROUP BY c.agents_name
        """, filter_values, as_dict=True)
        for entry in query:
            if entry.get("time_duration"):
                seconds = entry.get("time_duration")
                entry['time_duration'] = convert_seconds_to_hr_min_sec(seconds)
        data.extend(query)

    elif filters.get("based_on") == "Campaign":
        query1 = frappe.db.sql(f"""
            SELECT 
                c.campaign,
                a.parent_agents AS parent,
                ca.company,
                COUNT(*) AS all_calls,
                SUM(CASE WHEN c.status = 'Completed' AND c.call_disposal = 'Lead Created' THEN 1 ELSE 0 END) AS successful_calls,
                SUM(CASE WHEN c.status = 'No-Answer' AND c.call_disposal = 'No Answer' THEN 1 ELSE 0 END) AS unanswered_calls,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Hang up' THEN 1 ELSE 0 END) AS hang_up,
                SUM(CASE WHEN c.status = 'Completed' THEN 1 ELSE 0 END) AS completed_calls,
                SUM(CASE WHEN c.status = 'Cancelled' AND c.is_daily_limit_reach = 1 THEN 1 ELSE 0 END) AS other,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Call Back' THEN 1 ELSE 0 END) AS call_backs_requested,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Answering Machine -' THEN 1 ELSE 0 END) AS answering_machine,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Not Interested' THEN 1 ELSE 0 END) AS not_interested,
                SUM(CASE WHEN c.status IS NOT NULL THEN TIMESTAMPDIFF(SECOND, c.start_time_, c.end_time_) ELSE 0 END) AS time_duration,
                SUM(CASE WHEN c.status IS NOT NULL AND p.dnc = 1 THEN 1 ELSE 0 END) AS dnc_check_box,
                SUM(CASE WHEN c.status = 'Scheduled' THEN 1 ELSE 0 END) AS scheduled_calls
            FROM `tabCall` AS c
            LEFT JOIN `tabAgents` AS a ON c.agents_name = a.name
            LEFT JOIN `tabCampaign Contact` AS p ON c.contact = p.name
            LEFT JOIN `tabCampaigns` AS ca ON ca.name = c.campaign
            WHERE {conditions}
            GROUP BY c.campaign
        """, filter_values, as_dict=True)
        for entry in query1:
            if entry.get("time_duration"):
                seconds = entry.get("time_duration")
                entry['time_duration'] = convert_seconds_to_hr_min_sec(seconds)
        data.extend(query1)

    elif filters.get("based_on") == "Supervisor":
        query2 = frappe.db.sql(f"""
            SELECT 
                a.parent_agents AS parent,
                ca.company,
                COUNT(*) AS all_calls,
                SUM(CASE WHEN c.status = 'Completed' AND c.call_disposal = 'Lead Created' THEN 1 ELSE 0 END) AS successful_calls,
                SUM(CASE WHEN c.status = 'No-Answer' AND c.call_disposal = 'No Answer' THEN 1 ELSE 0 END) AS unanswered_calls,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Hang up' THEN 1 ELSE 0 END) AS hang_up,
                SUM(CASE WHEN c.status = 'Completed' THEN 1 ELSE 0 END) AS completed_calls,
                SUM(CASE WHEN c.status = 'Cancelled' AND c.is_daily_limit_reach = 1 THEN 1 ELSE 0 END) AS other,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Call Back' THEN 1 ELSE 0 END) AS call_backs_requested,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Answering Machine -' THEN 1 ELSE 0 END) AS answering_machine,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Not Interested' THEN 1 ELSE 0 END) AS not_interested,
                SUM(CASE WHEN c.status IS NOT NULL THEN TIMESTAMPDIFF(SECOND, c.start_time_, c.end_time_) ELSE 0 END) AS time_duration,
                SUM(CASE WHEN c.status IS NOT NULL AND p.dnc = 1 THEN 1 ELSE 0 END) AS dnc_check_box,
                SUM(CASE WHEN c.status = 'Scheduled' THEN 1 ELSE 0 END) AS scheduled_calls
            FROM `tabCall` AS c
            LEFT JOIN `tabAgents` AS a ON c.agents_name = a.name
            LEFT JOIN `tabCampaign Contact` AS p ON c.contact = p.name
            LEFT JOIN `tabCampaigns` AS ca ON ca.name = c.campaign
            WHERE {conditions}
            GROUP BY a.parent_agents
        """, filter_values, as_dict=True)
        for entry in query2:
            if entry.get("time_duration"):
                seconds = entry.get("time_duration")
                entry['time_duration'] = convert_seconds_to_hr_min_sec(seconds)
        data.extend(query2)

    elif filters.get("based_on") == "Customer":
        query3 = frappe.db.sql(f"""
            SELECT 
                c.customer_name,
                ca.company,
                COUNT(*) AS all_calls,
                SUM(CASE WHEN c.status = 'Completed' AND c.call_disposal = 'Lead Created' THEN 1 ELSE 0 END) AS successful_calls,
                SUM(CASE WHEN c.status = 'No-Answer' AND c.call_disposal = 'No Answer' THEN 1 ELSE 0 END) AS unanswered_calls,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Hang up' THEN 1 ELSE 0 END) AS hang_up,
                SUM(CASE WHEN c.status = 'Completed' THEN 1 ELSE 0 END) AS completed_calls,
                SUM(CASE WHEN c.status = 'Cancelled' AND c.is_daily_limit_reach = 1 THEN 1 ELSE 0 END) AS other,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Call Back' THEN 1 ELSE 0 END) AS call_backs_requested,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Answering Machine -' THEN 1 ELSE 0 END) AS answering_machine,
                SUM(CASE WHEN c.status IS NOT NULL AND c.call_disposal = 'Not Interested' THEN 1 ELSE 0 END) AS not_interested,
                SUM(CASE WHEN c.status IS NOT NULL THEN TIMESTAMPDIFF(SECOND, c.start_time_, c.end_time_) ELSE 0 END) AS time_duration,
                SUM(CASE WHEN c.status IS NOT NULL AND p.dnc = 1 THEN 1 ELSE 0 END) AS dnc_check_box,
                SUM(CASE WHEN c.status = 'Scheduled' THEN 1 ELSE 0 END) AS scheduled_calls
            FROM `tabCall` AS c
            LEFT JOIN `tabCampaign Contact` AS p ON c.contact = p.name
            LEFT JOIN `tabCampaigns` AS ca ON ca.name = c.campaign
            WHERE {conditions}
            GROUP BY c.customer_name
        """, filter_values, as_dict=True)
        for entry in query3:
            if entry.get("time_duration"):
                seconds = entry.get("time_duration")
                entry['time_duration'] = convert_seconds_to_hr_min_sec(seconds)
        data.extend(query3)

    return data

def get_chart(data, filters):
    labels = []
    datasets = [
        {
            'name': 'All Calls',
            'values': []
        },
        {
            'name': 'Successful Calls',
            'values': []
        },
        {
            'name': 'Unanswered Calls',
            'values': []
        },
        {
            'name': 'Hang-up',
            'values': []
        },
        {
            'name': 'Completed Calls',
            'values': []
        },
        {
            'name': 'Call Backs Requested',
            'values': []
        },
        {
            'name': 'Answering Machine',
            'values': []
        },
        {
            'name': 'Not Interested',
            'values': []
        },
        {
            'name': 'Other',
            'values': []
        },
        {
            'name': 'Scheduled Calls',
            'values': []
        },
        {
            'name': 'DNC',
            'values': []
        },
    ]

    if filters.get("based_on") == "Agent":
        labels = [d.get("agents_name") for d in data]
    elif filters.get("based_on") == "Campaign":
        labels = [d.get("campaign") for d in data]
    elif filters.get("based_on") == "Supervisor":
        labels = [d.get("parent") for d in data]
    elif filters.get("based_on") == "Customer":
        labels = [d.get("customer_name") for d in data]

    for d in data:
        datasets[0]['values'].append(d.get("all_calls"))
        datasets[1]['values'].append(d.get("successful_calls"))
        datasets[2]['values'].append(d.get("unanswered_calls"))
        datasets[3]['values'].append(d.get("hang_up"))
        datasets[4]['values'].append(d.get("completed_calls"))
        datasets[5]['values'].append(d.get("call_backs_requested"))
        datasets[6]['values'].append(d.get("answering_machine"))
        datasets[7]['values'].append(d.get("not_interested"))
        datasets[8]['values'].append(d.get("other"))
        datasets[9]['values'].append(d.get("scheduled_calls"))
        datasets[10]['values'].append(d.get("dnc_check_box"))

    chart = {
        'data': {
            'labels': labels,
            'datasets': datasets
        },
        'type': 'bar',
        'height': 300,
        'colors': ['#7cd6fd', '#743ee2', '#5e64ff']
    }
    return chart

def convert_seconds_to_hr_min_sec(seconds):
    try:
        duration = timedelta(seconds=seconds)
        return str(duration)
    except Exception as e:
        return str(seconds)
