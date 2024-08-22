frappe.ui.form.on("Sales Invoice", {
    refresh:function(frm){
         frm.add_custom_button('Get Campaign', function() {
            erpnext.utils.map_current_doc({
                method: "b2b_marketing.b2b_marketing.doctype.invoice_build_up.invoice_build_up.make_campaign_invoice",
                source_doctype: "Invoice Build Up",
                target: frm,
                setters: {
						customer: me.frm.doc.customer || undefined,
						campaigns: me.frm.doc.campaigns || undefined,
						campaigns_name: me.frm.doc.campaigns_name || undefined,
				},
                get_query_filters: {
                    status:"To Bill"
                }
            })
         }, __("Get items from"));
    }
});