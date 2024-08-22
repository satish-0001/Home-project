// Copyright (c) 2019, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Size', {
	validate: function(frm) {
	     if (frm.doc.min_employee > frm.doc.max_employee) {
            frappe.msgprint(__("Please set Maximum Employee Size greater than the Minimum Employee Size"));
            frappe.validated = false;
        }
	 }
});
