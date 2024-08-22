// Copyright (c) 2023, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Campaign Organization', {
	onload: function(frm) {
		if(frm.doc.revenue_currency){
			frm.set_currency_labels(['annual_revenue'], frm.doc.revenue_currency)
			// frm.set_df_property("annual_revenue","read_only",1)
		}

		frm.set_query("sub_industry", function() {
			return {
			   filters: {
					"main_industry":frm.doc.industry,
					"disabled":0
				}
			}
		});
	},
	refresh: function(frm) {
		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Campaign Organization'};
		
 
	 },
});


