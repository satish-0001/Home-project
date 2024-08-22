// Copyright (c) 2019, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Campaign Lead', {
	 refresh: function(frm) {
        frm.add_custom_button(__('Show Call Detail'), function() {
				frappe.set_route('List', 'Call', {name: frm.doc.call});
			});
	 },
	//  contact:function(frm){
    //     return frm.call('get_email_phone_number').then(() => {
    //         frm.refresh_field('phone_number');
    //         frm.refresh_field('email');
    //     });
    // }

});
