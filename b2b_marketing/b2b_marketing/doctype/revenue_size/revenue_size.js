// Copyright (c) 2019, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Revenue Size', {
	 validate: function(frm) {
	     if (frm.doc.min_revenue > frm.doc.max_revenue) {
            frappe.msgprint(__("Please set Maximum Revenue greater than the Minimum Revenue"));
            frappe.validated = false;
        }
	 }
});
