// Copyright (c) 2020, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Viva Communication', {
	 onload: function(frm) {
        frm.trigger('set_property');
	 },
	 set_property: function(frm) {
         if(frm.doc.enable ==1)
         {
            frm.set_df_property("api_key", "reqd", 1);
            frm.set_df_property("secret_key", "reqd", 1);
         }
         else
         {
            frm.set_df_property("api_key", "reqd", 0);
            frm.set_df_property("secret_key", "reqd", 0);
         }
     },
     enable: function (frm) {
		frm.trigger('set_property');
	},
});
