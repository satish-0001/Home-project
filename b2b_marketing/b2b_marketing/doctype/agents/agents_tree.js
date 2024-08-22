frappe.treeview_settings["Agents"] = {
	fields: [
		{fieldtype:'Data', fieldname: 'agents_name',
			label:__('New Agent Name'), reqd:true},
		{fieldtype:'Link', fieldname:'employee',
			label:__('Employee'), options:'Employee',
			description: __("Please enter Employee Id of this Agent")},
		{fieldtype:'Check', fieldname:'is_group', label:__('Group Node'),
			description: __("Further nodes can be only created under 'Group' type nodes")}
	],
}