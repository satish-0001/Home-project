frappe.ui.form.on("Quality Review", {
    onload:function(frm){
        frm.set_query("quality_type", function() {
		    return {
                filters:
                [
                    ['DocType', 'name', 'in','Campaign Organization, Campaign Contact, Campaign Lead, Call, Address']
                ]
            }
        });
        frm.trigger('set_properties');
    },
    setup: function(frm){
        frm.fields_dict['reviews'].grid.get_field("quality_points").get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {
                filters:[
                       ['Quality Points', 'quality_goal', '=', frm.doc.goal]
		            ]
            }
        }
    },
    validate:function(frm){
        if (!frm.doc.__islocal)
            {

        if (!cur_frm.doc.quaity_done_by)
            {
            var anyFailed = false;
            frm.doc.reviews.forEach(function(row,index) {
                if (row.status == 'Open') {
                    var rowNumber = index + 1;
                    frappe.throw("Status field in row " + rowNumber + " must be 'Passed' or 'Failed'");
                }
                if (row.status === "Failed") {
                    anyFailed = true;
                    return false;
                }
            });
            if (anyFailed) {
                frm.set_value("result", "Disqualified");
            } else {
                frm.set_value("result", "Qualified");
            }
        }
    }
    },
    refresh:function(frm){
        if (!cur_frm.doc.quaity_done_by)
            {
        if (cur_frm.doc.result)
            {
                frm.add_custom_button(__('Submit'), function(){
                    frm.doc.reviews.forEach(function(row,index) {
                        if (!row.quality_rating) {
                            var rowNumber = index + 1;
                            frappe.throw("Before Submitting the Quality Review, please set Quality ratings in row " + rowNumber);
                        }
                    });
                    frm.call({
                        method:"b2b_marketing.b2b_marketing.doctype.call.call.set_quality_rating",
                        args: {
                            doc_name: frm.doc.name,
                            result: frm.doc.result
                        },
                            callback: function(r){
                                frm.trigger('set_properties');
                                if (!cur_frm.doc.quaity_done_by && frappe.session.user)
                                    {
                                        frm.set_value('quaity_done_by',frappe.session.user)
                                        frm.save()
                                    }                            
                            }
                        });
                }).addClass('btn-primary');
            }
        }
        if(cur_frm.doc.result && cur_frm.doc.quaity_done_by)
            {
                frm.disable_save();
            }
        if(!frm.doc.__islocal)
        {
            if(frm.doc.contact)
            {
                frm.add_custom_button(__('Edit Contact'), function()
                {
                    frappe.route_options = {doc_type: "Quality Review",doc_name: frm.doc.name};
                    frappe.set_route("Form", "Campaign Contact",frm.doc.contact);
                }).addClass('btn-info');
            }
            cur_frm.cscript.get_campaign_customer_contact()
        }

    },
    set_properties:function(frm){
        if (frm.doc.quaity_done_by)
        {
             frm.set_df_property("goal", "read_only", 1);
             frm.set_df_property("value", "read_only", 1);
             frm.set_df_property("quality_type", "read_only", 1);
             frm.set_df_property("contact", "read_only", 1);
             frm.set_df_property("reviews", "read_only", 1);
             frm.set_df_property("comment", "read_only", 1);
             frm.set_df_property("feedback", "read_only", 1);
             frm.set_df_property("additional_information", "read_only", 1);
             frm.set_df_property("area_of_improvement_1", "read_only", 1);
             frm.set_df_property("area_of_improvement_2", "read_only", 1);
             frm.set_df_property("area_of_improvement_3", "read_only", 1);
             frm.set_df_property("result", "read_only", 1);
             frm.set_df_property("quaity_done_by", "read_only", 1);
        }
    },
    quality_type: function(frm){
        if(frm.doc.quality_type == "Contact"){
            frm.set_query("value", function() {
		    return {
                filters:{
                    "is_b2b_contact":1,
                }
            }
        });
        }else{
            frm.set_query("value", function() {
                return {
                    filters:
                    [
                        ['docstatus', '!=', '2']
                    ]
                }
            });
        }
    },

    value: function(frm) {
        if (frm.doc.quality_type === "Call") {
            frappe.call({
                method: "b2b_marketing.b2b_marketing.doctype.custom_quality_review.call_update_fields",
                args: {
                    call: frm.doc.value
                },
                callback: function(response) {
                    if (response.message) {
                        console.log("Response:", response.message);
                        frm.set_value("contact", response.message.contact);

                        var departments = response.message.department.join(", ");
                        frm.set_value("custom_department", departments);

                        var titles = response.message.title.join(", ");
                        frm.set_value("job_position", titles);

                        frm.refresh();
                    }
                }
            });
        }
        if (frm.doc.quality_type === "Campaign Contact"){
            frappe.call({
                method: "b2b_marketing.b2b_marketing.doctype.custom_quality_review.contact_update",
                args: {
                    contact: frm.doc.value
                },
                callback: function(response) {
                    if (response.message) {
                        console.log("Response:", response.message);
                        frm.set_value("contact", frm.doc.value);

                        var departments = response.message.department.join(", ");
                        frm.set_value("custom_department", departments);

                        var titles = response.message.title.join(", ");
                        frm.set_value("job_position", titles);

                        frm.refresh();
                    }
                }
            });

        }
    }

});

frappe.ui.form.on('Quality Review Objective', {
    quality_points: function(frm, cdt, cdn) {
        let child = locals[cdt][cdn];
        if (child.quality_points) {
            frappe.db.get_value('Quality Points', {"name": child.quality_points}, 'marks')
                .then(r => {
                    let marks = r.message.marks;
                    if (marks !== undefined) {
                        let quality_rating_floor = custom_round((marks / 100) * 5);
                        let rating = quality_rating_floor / 5;
                        frappe.model.set_value(cdt, cdn, 'quality_rating', rating);
                    }
                });
        }
    }
});

function custom_round(number) {
    var fractional_part = number - Math.floor(number);
    if (fractional_part <= 0.4) {
        return Math.floor(number);
    } else if (fractional_part >= 0.6) {
        return Math.ceil(number);
    } else {
        return number;
    }
}

cur_frm.cscript.get_campaign_customer_contact= function(){
    return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.get_campaign_customer_contact",
        args: {
            quality_type: cur_frm.doc.quality_type,
            value: cur_frm.doc.value,
            doc_name : cur_frm.doc.name
         },
         callback: function(r){
            cur_frm.refresh_field('campaign');
            cur_frm.refresh_field('customer');
            cur_frm.refresh_field('contact');
        }
    });
}