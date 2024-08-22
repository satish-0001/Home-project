// Copyright (c) 2020, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Invoice Build Up', {
    refresh: function(frm) {
            frm.disable_save()
	 },
	onload:function(frm){
        frm.set_query("based_on", function() {
		    return {
                filters:
                [
                    ['DocType', 'name', 'in','Campaign Lead, Call']
                ]
            }
        });
        frm.set_query('supervisor', function(doc) {
            return {
                filters: {
                    "is_group":1,
                }
            };
        });
    }
});
