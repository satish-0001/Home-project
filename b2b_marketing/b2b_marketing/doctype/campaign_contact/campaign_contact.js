// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Campaign Contact', {
	before_save: function(frm) {
		if(frm.doc.first_name && frm.doc.last_name){
			var full_name = frm.doc.first_name + " "+frm.doc.last_name
			frm.set_value("full_name",full_name)
			frm.refresh_field("full_name")
		}	
		else{
			var full_name = frm.doc.first_name
			frm.set_value("full_name",full_name)
			frm.refresh_field("full_name")
		}	

	},
	before_load: function (frm) {
		let update_tz_options = function () {
			frm.fields_dict.timezone.set_data(frappe.all_timezones);
		};

		if (!frappe.all_timezones) {
			frappe.call({
				method: "frappe.core.doctype.user.user.get_timezones",
				callback: function (r) {
					frappe.all_timezones = r.message.timezones;
					update_tz_options();
				},
			});
		} else {
			update_tz_options();
		}
	},
});
