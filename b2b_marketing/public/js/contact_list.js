
frappe.listview_settings['Contact'] = {
    filters: [["is_b2b_contact", "=", "1"]],
    onload: function(me) {
        console.log("**********************cur list",cur_list)
//		me.page.add_action_item('Add to Campaign Designer', function() {
//			const contact = me.get_checked_items();
//			frappe.call({
//				method: "b2b_marketing.b2b_marketing.doctype.campaigns_designer.campaigns_designer.get_contact_list",
//				freeze: true,
//				args:{
//					"contact": contact
//				},
//				callback: function (r) {
//					if (r.message)
//					{
//						frappe.set_route("Form", "Campaigns Designer", r.message);
//						window.location.reload();
//					}
//				}
//			});
//		});
//		frappe.route_options = {
//			"is_b2b_contact":1
//		};
	},
}