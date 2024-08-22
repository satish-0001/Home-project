// Copyright (c) 2020, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lead Per Organization', {
	 refresh: function(frm) {
            frm.disable_save()
	 },
});
