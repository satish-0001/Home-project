frappe.ui.form.on("Contact", {
    onload:function(frm){

        frm.set_query("job_function", function() {
		    return {
                filters:{
                    "department":frm.doc.department_id,
                }
            }
        });
    },
    refresh:function(frm){
        if(!frm.doc.__islocal)
        {
            frm.add_custom_button(__('Create Call'), function()
            {
                frappe.new_doc('Call',{contact: frm.doc.name});

            }).addClass('btn-primary');
        }
    },
    validate:function(frm){
//        const doc_type = frappe.route_options.doc_type
//        const doc_name = frappe.route_options.doc_name
//        if(doc_type && doc_name)
//        {
//            frappe.route_options = { refresh_call: "refresh_call"}
//            frappe.set_route("Form", doc_type, doc_name);
//        }

    }
});