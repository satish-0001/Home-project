// Copyright (c) 2020, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Organization Creation Tool', {
	setup:function(frm){



		frappe.realtime.on("data_import_progress", (data) => {
			if (data.data_import !== frm.doc.name) {
				return;
			}
			let percent = Math.floor((data.current * 100) / data.total);
			let seconds = Math.floor(data.eta);
			let minutes = Math.floor(data.eta / 60);
			let eta_message =
				// prettier-ignore
				seconds < 60
					? __('About {0} seconds remaining', [seconds])
					: minutes === 1
						? __('About {0} minute remaining', [minutes])
						: __('About {0} minutes remaining', [minutes]);

			let message;
			if (data.success) {
				let message_args = [data.current, data.total,eta_message];
				message = __("Importing {0} of {1}, {2}", message_args)
						
			}
			frm.dashboard.show_progress(
				__("Organization Import"),
				percent,
				message
			);

		})
	},
	refresh: function(frm) {
		frm.call({
			doc:frm.doc,
			method:'select_check'
		})
		// frm.disable_save();
		if (!frm.doc.__islocal && frm.doc.status!="Success") {

		// frm.page.set_primary_action(__('Create Organization'), () => {
			
		// 	let btn_primary = frm.page.btn_primary.get(0);
		// 	return frm.call({
		// 		doc: frm.doc,
		// 		btn: $(btn_primary),
		// 		method: "make_organization",
		// 		callback: (r) => {
		// 			if(!r.exc){
		// 				frm.refresh_fields();
		// 				frm.reload_doc();
		// 			}
		// 		}
		// 	});
		// });
	}
	},
});




