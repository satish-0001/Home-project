frappe.ui.form.on('Campaign Assets', {
	// refresh: function(frm) {

	// },
	onload: function(frm) {
		frm.trigger('set_url_filter');
	},
	 set_url_filter: function(frm) {
        if(frm.doc.asset_type =="URL")
        {
            frm.set_df_property("enter_url", "reqd", 1);
            frm.set_df_property("attachment", "reqd", 0);
            frm.set_df_property("enter_url", "read_only", 0);
            frm.set_df_property("attachment", "read_only",1);
        }
        if(frm.doc.asset_type =="Attachment")
        {
            frm.set_df_property("enter_url", "reqd", 0);
            frm.set_df_property("attachment", "reqd", 1);
            frm.set_df_property("enter_url", "read_only", 1);
            frm.set_df_property("attachment", "read_only",0);
        }
	 },
	 asset_type: function (frm) {
		frm.trigger('set_url_filter');
	}
});