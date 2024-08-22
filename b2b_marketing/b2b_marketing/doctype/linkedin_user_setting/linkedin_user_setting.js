// Copyright (c) 2020, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('LinkedIn User Setting', {
	 enable: function(frm) {
	    if(frm.doc.enable ==1){
	        return frm.call('check_validation')
	    }
	 }
});
