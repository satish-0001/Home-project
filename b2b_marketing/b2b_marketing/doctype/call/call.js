// Copyright (c) 2019, Dexciss and contributors
// For license information, please see license.txt

frappe.provide('frappe.phone_call');
frappe.provide('frappe.twilio_conn_dialog_map')
let device;
frappe.ui.form.on('Call', {
    onload: function(frm){
        if(frm.doc.status != "Scheduled"){
            frm.set_df_property('call_phone', 'read_only', 1);
			frm.set_df_property('mobile_phone', 'read_only', 1);
			frm.set_df_property('corporate_phone', 'read_only', 1);
			frm.set_df_property('organization_phone', 'read_only', 1);
        }else{
			frm.set_df_property('call_phone', 'read_only', 0);
			frm.set_df_property('mobile_phone', 'read_only', 0);
			frm.set_df_property('corporate_phone', 'read_only', 0);
			frm.set_df_property('organization_phone', 'read_only', 0);
        }
    },
	refresh: function(frm) {
       if(frm.doc.status != "Scheduled"){
            frm.set_df_property('phone', 'read_only', 1);
			frm.set_df_property('mobile_phone', 'read_only', 1);
			frm.set_df_property('corporate_phone', 'read_only', 1);
			frm.set_df_property('organization_phone', 'read_only', 1);
        }else{
			frm.set_df_property('phone', 'read_only', 0);
			frm.set_df_property('mobile_phone', 'read_only', 0);
			frm.set_df_property('corporate_phone', 'read_only', 0);
			frm.set_df_property('organization_phone', 'read_only', 0);
        }
	     if(!frm.doc.__islocal)
         {
             frm.disable_save()

         }
         if(!frm.doc.__islocal && (!frm.doc.is_daily_limit_reach && !frm.doc.is_organization_limit_reach) && !frm.doc.call_disposal)
         {
             frm.add_custom_button('Edit Contact', function() {
				var contact = frm.doc.contact
				var organization = frm.doc.organization
					frappe.db.get_doc("Campaign Contact",contact).then(ct => {
						d.fields_dict.first_name.set_value(ct.first_name)
						d.fields_dict.last_name.set_value(ct.last_name)
						d.fields_dict.department.set_value(ct.department)
						d.fields_dict.email.set_value(ct.email)
						d.fields_dict.corporate_phone.set_value(ct.corporate_phone)
						d.fields_dict.phone.set_value(ct.phone)
						d.fields_dict.mobile_phone.set_value(ct.mobile_phone)
					})
					frappe.db.get_doc("Campaign Organization",organization).then(org => {
						d.fields_dict.name.set_value(org.name)
						d.fields_dict.company_phone.set_value(org.company_phone)
						d.fields_dict.employees.set_value(org.employees)
						d.fields_dict.annual_revenue.set_value(org.annual_revenue)
						d.fields_dict.industry.set_value(org.industry)
						d.fields_dict.sub_industry.set_value(org.sub_industry)
						d.fields_dict.website.set_value(org.website)
						d.fields_dict.domain.set_value(org.domain)
					})
				const  d = new frappe.ui.Dialog({
					title: 'Edit Contact/Organization',
					fields: [
						{fieldtype:"Section Break", label: __("Edit Contact")},
						{
							label: 'First name',
							fieldname: 'first_name',
							fieldtype: 'Data'
						},
						{fieldtype:"Column Break"},
						{
							label: 'Last Name',
							fieldname: 'last_name',
							fieldtype: 'Data'
						},
						{fieldtype:"Section Break"},
						{
							label: 'Department',
							fieldname: 'department',
							fieldtype: 'Link',
							options:"Department"
						},
						{fieldtype:"Column Break"},
						{
							label: 'Email',
							fieldname: 'email',
							fieldtype: 'Data'
						},
						
						{fieldtype:"Section Break"},
						{
							label: 'Corporate Phone',
							fieldname: 'corporate_phone',
							fieldtype: 'Data'
						},
						{fieldtype:"Column Break"},
						{
							label: 'Phone',
							fieldname: 'phone',
							fieldtype: 'Data'
						},
						{fieldtype:"Column Break"},
						{
							label: 'Mobile Phone',
							fieldname: 'mobile_phone',
							fieldtype: 'Data'
						},
						// {fieldtype:"Column Break"},
						{fieldtype:"Section Break", label: __("Edit Organization")},

						{
							label: 'Organization Name',
							fieldname: 'name',
							fieldtype: 'Link',
							options:"Campaign Organization",
							read_only:1
						},
						{fieldtype:"Column Break"},
						{
							label: 'Company Phone',
							fieldname: 'company_phone',
							fieldtype: 'Data'
						},
						{fieldtype:"Column Break"},
						{
							label: '#Employees',
							fieldname: 'employees',
							fieldtype: 'Data'
						},
						{fieldtype:"Section Break"},
						{
							label: 'Revenue',
							fieldname: 'annual_revenue',
							fieldtype: 'Currency'
						},
						{fieldtype:"Column Break"},
						{
							label: 'Industry',
							fieldname: 'industry',
							fieldtype: 'Link',
							options:"Industry Type"

						},
						{fieldtype:"Column Break"},
						{
							label: 'Sub Industry',
							fieldname: 'sub_industry',
							fieldtype: 'Link',
							options:"Sub Industry Type"

						},
						{fieldtype:"Section Break"},
						{
							label: 'Website',
							fieldname: 'website',
							fieldtype: 'Data',
							options:"URL"
						},
						{fieldtype:"Column Break"},
						{
							label: 'Domain',
							fieldname: 'domain',
							fieldtype: 'Data',
							options:"URL"
						},
					],
					primary_action_label: 'Submit',
					primary_action(values) {
						console.log(values);
						frappe.call({
							method:"b2b_marketing.b2b_marketing.doctype.call.call.update_ct_org",
							args:{
								"contact":frm.doc.contact,
								"organization":frm.doc.organization,
								"values":values,
								"doc_id":frm.doc.name
							},
							callback: function(response) {
								frappe.msgprint("Campaign Contact and Organization Details Updated")
								window.location.reload() 
								// if (response.message) {
								// 	// Update the current form with the response data
								// 	frm.refresh_field("fieldname"); // Replace "fieldname" with the appropriate fieldname to refresh
								// } else {
								// 	frappe.msgprint("Failed to update. Please try again.");
								// }
							}
						})
						d.hide();
					}
				});
				d.show();
			 }).addClass('btn-info');
             frm.add_custom_button('Script', function() {
                    cur_frm.cscript.get_campaign_script()
             });
         }
         if(!frm.doc.__islocal && !frm.doc.is_daily_limit_reach && !frm.doc.is_organization_limit_reach)
         {
            frm.add_custom_button('Send Assets', function() {
                cur_frm.cscript.send_assets()
            });
			frappe.model.get_value('Campaigns Designer', {'name': frm.doc.campaigns_name}, 'auto_send_email', function(value) {
			if (value.auto_send_email == 0) {
				frm.add_custom_button('Send Template Email', function() {

							cur_frm.cscript.send_mail()
						})
			}
		});		
		// 	// if (frm.doc.email_template)
		// 	// 	{
		// 	// frm.add_custom_button('Send Template Email', function() {

		// 	// 	cur_frm.cscript.send_mail()
		// 	// })
		// }
        }
	},

    contact:function(frm){
		var phones = []
        if(frm.doc.contact){
			phones.push(frm.doc.mobile_phone)
			phones.push(frm.doc.phone_number)
			phones.push(frm.doc.corporate_phone)

		}
    },

});
cur_frm.cscript.change_status_start = function()
 {
     cur_frm.set_value("start_call",1);
	 console.log("START CALL")
     return cur_frm.call({
         method:"b2b_marketing.b2b_marketing.doctype.call.call.check_limit",
         args: {
                doc: cur_frm.doc
               },
         callback: function(r)
             {
                 if (r.message)
                 {
                   
                     cur_frm.set_value("start_time_",r.message);

                     cur_frm.save();
                 }
             }
     });
 };
 cur_frm.cscript.change_status_schedule= function()
 {
     cur_frm.set_value("status", "On-going");
	 var currentDateTime = frappe.datetime.now_datetime();
     cur_frm.set_value("start_time_",currentDateTime);
     cur_frm.save();
 };
cur_frm.cscript.change_status_no_answer= function()
 {
    cur_frm.set_value("status", "No-Answer");
    cur_frm.save();
 };
cur_frm.cscript.change_status_complete= function()
 {
    cur_frm.set_value("status", "Completed");
	var currentDateTime = frappe.datetime.now_datetime();

	// var today = new Date();
	// var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
	// var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
	// var dateTime = date+' '+time;
    cur_frm.set_value("end_time_",currentDateTime);
    cur_frm.set_value("completed_by",frappe.session.user);
    cur_frm.save();
	cur_frm.refresh()

    var d = new frappe.ui.Dialog({
//			title: __('Update Cost Center Number'),
			static: 1,
			fields: [
				{
					"label": 'Create Lead',
					"fieldname": "create_lead",
					"fieldtype": "Button",
				},
				{
					"label": 'Call Back',
					"fieldname": "call_back",
					"fieldtype": "Button",
				},
				{
					"label": 'Answering Machine - Prospect',
					"fieldname": "answering_machine_prospect",
					"fieldtype": "Button",
				},
				{
					"label": 'Answering Machine - Operator',
					"fieldname": "answering_machine_operator",
					"fieldtype": "Button",
				},
				{
					"fieldname": "cb1",
					"fieldtype": "Column Break",
				},
				{
					"label": 'No Answer',
					"fieldname": "no_answer",
					"fieldtype": "Button",
				},
				{
					"label": 'Hang up',
					"fieldname": "hang_up",
					"fieldtype": "Button",
				},
				{
					"label": 'Not Interested',
					"fieldname": "not_interested",
					"fieldtype": "Button",
				},
				{
					"label": 'DNC',
					"fieldname": "dnc",
					"fieldtype": "Button",
				},
				{
					"label": 'Wrong Number',
					"fieldname": "wrong_number",
					"fieldtype": "Button",
				}
			],
	    });
	    d.get_close_btn().hide();
	    d.fields_dict.create_lead.$input.click(function() {
            d.hide();
            cur_frm.cscript.create_lead()
            cur_frm.cscript.build_invoice()
            return cur_frm.call('update_agent_status')
	    });

	    d.fields_dict.call_back.$input.click(function() {
            d.hide();
            frappe.run_serially([
                () => cur_frm.set_value("call_disposal","Call Back"),
                () => cur_frm.cscript.check_quality_review_in_camp_design("Call Back"),
                () => cur_frm.cscript.build_invoice(),
                () => cur_frm.cscript.create_new_call(),
                () => cur_frm.save(),
                () => {
                    return cur_frm.call('update_agent_status')
                }
	        ]);


	    });

	    d.fields_dict.answering_machine_prospect.$input.click(function() {
            d.hide();
            cur_frm.set_value("call_disposal","Answering Machine - Prospect");
            cur_frm.cscript.check_quality_review_in_camp_design("Answering Machine - Prospect");
            cur_frm.cscript.build_invoice()
            cur_frm.save();
            return cur_frm.call('update_agent_status')
	    });

	    d.fields_dict.answering_machine_operator.$input.click(function() {
            d.hide();
            cur_frm.set_value("call_disposal","Answering Machine - Operator");
            cur_frm.cscript.check_quality_review_in_camp_design("Answering Machine - Operator");
            cur_frm.cscript.build_invoice()
            cur_frm.save();
            return cur_frm.call('update_agent_status')
	    });

	    d.fields_dict.no_answer.$input.click(function() {
            d.hide();
            cur_frm.set_value("call_disposal","No Answer");
            cur_frm.cscript.check_quality_review_in_camp_design("No Answer");
            cur_frm.cscript.change_status_no_answer()
            cur_frm.cscript.build_invoice()
            return cur_frm.call('update_agent_status')
	    });

	    d.fields_dict.hang_up.$input.click(function() {
            d.hide();
            cur_frm.set_value("call_disposal","Hang up");
            cur_frm.cscript.check_quality_review_in_camp_design("Hang up");
            cur_frm.cscript.build_invoice()
            cur_frm.save();
            return cur_frm.call('update_agent_status')
	    });

	    d.fields_dict.not_interested.$input.click(function() {
            d.hide();
            cur_frm.set_value("call_disposal","Not Interested");
            cur_frm.cscript.check_quality_review_in_camp_design("Not Interested");
            cur_frm.cscript.build_invoice()
            cur_frm.save();
            return cur_frm.call('update_agent_status')
	    });

	    d.fields_dict.dnc.$input.click(function() {
            d.hide();
            return cur_frm.call({
                 method:"b2b_marketing.b2b_marketing.doctype.call.call.set_contact_dnc",
                 args: {
                        doc_name: cur_frm.doc.contact
                       },
                 callback: function(r)
                     {
						cur_frm.set_value("call_disposal","DNC");
                         cur_frm.cscript.check_quality_review_in_camp_design("DNC");
                         cur_frm.cscript.build_invoice()
                         cur_frm.save();
                         return cur_frm.call('update_agent_status')
                     }
            });
	    });

		d.fields_dict.wrong_number.$input.click(function() {
            d.hide();
            return cur_frm.call({
                 method:"b2b_marketing.b2b_marketing.doctype.call.call.set_contact_wrong_number",
                 args: {
                        doc_name: cur_frm.doc.contact
                       },
                 callback: function(r)
                     {
						 cur_frm.set_value("call_disposal","Wrong Number");
                         cur_frm.cscript.check_quality_review_in_camp_design("DNC");
                         cur_frm.cscript.build_invoice()
                         cur_frm.save();
                         return cur_frm.call('update_agent_status')
                     }
            });
	    });
	    d.show();
	    d.get_close_btn().on('click', () => {
	        if(cur_frm.doc.status == "Completed"){
	            cur_frm.set_value("status", "Scheduled");
                cur_frm.set_value("end_time_", false);
                cur_frm.set_value("completed_by",false);
                cur_frm.save();
	        }else{
	            console.log("-------onnnnnnnn",cur_frm.doc.status);
	            cur_frm.set_value("status", "On-going");
                cur_frm.set_value("end_time_", false);
                cur_frm.set_value("completed_by",false);
                cur_frm.save();
	        }

		});

 };
cur_frm.cscript.create_lead = function()
 {
    return cur_frm.call({
         method:"b2b_marketing.b2b_marketing.doctype.call.call.create_lead",
         args: {
                doc: cur_frm.doc.name
               },
         callback: function(r)
             {
                 if (r.message)
                 {
                     cur_frm.reload_doc();
                 }
             }
			
    });
 };

// cur_frm.cscript.publish_form =function()
// {
//     return cur_frm.call({
//         method:"b2b_marketing.b2b_marketing.doctype.call.call.publish_form",
//         args: {
//                 doc: cur_frm.doc
//             },
//             callback: function(r)
//             {
//                 if((r.message).length > 0)
//                 {
//                     var dialog = new frappe.ui.Dialog({
//                     static: 1,
//                     minimizable: true,
//                     });
//                     dialog.get_close_btn().show();
//                     dialog.$body.append("<div id='mySurvey'></div><script>new TripettoCollectorRolling.run({"+
//                                     "element: document.getElementById('mySurvey'),"+
//                                     "definition:"+r.message[0]+","+
//                                     "onFinish: function(instance){"+
//                                     "const x = TripettoCollector.Export.fields(instance);"+
//                                     "frappe.xcall('tripetto_survey.tripetto_survey.page.tripetto_survey.tripetto_survey.set_answer',{docname:'"+r.message[1]+"',str_data:x}).then(e => {});"+
//                                     "} });</script>");
//                     dialog.show();
//                     document.getElementsByClassName("modal")[0].remove();
//                 }
//             }
//         });
// }

cur_frm.cscript.check_quality_review_in_camp_design =function(disposal){
     return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.check_quality_review_in_camp_design",
        args:{
                call_disposal: disposal,
                doc_name :cur_frm.doc.name
           },
        callback: function(r)
           {
           }
     });
}
cur_frm.cscript.build_invoice = function(){
    return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.build_invoice",
        args:{
                charge_type: "Charge Per Call",
                doc_name :cur_frm.doc.name,
                doc : "Call",
                voucher : cur_frm.doc.name
           },
        callback: function(r)
           {
           }
     });
}

cur_frm.cscript.get_campaign_script = function(){
    return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.get_campaign_script",
        args:{
                doc_name :cur_frm.doc.campaign
           },
        callback: function(r)
           {
                var dialog = new frappe.ui.Dialog({
                    title: __('Calling Script'),
                    'minimizable': true,
                });
                dialog.get_close_btn().show();
                dialog.$body.append(r.message);
                dialog.show();
           }
    });
}

cur_frm.cscript.create_new_call = function(){
    return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.create_new_call",
        args:{
                doc_name :cur_frm.doc.name
            },
        callback: function(r)
           {
           }
    });
}

cur_frm.cscript.send_assets =function(){


	let data_x=[]
                    let d = new frappe.ui.Dialog({
                        title: 'Send Email',
                        fields: [
                            {
                                label: __('Assests'),
                                fieldname: 'assests',
                                fieldtype: 'Table',
                                reqd: 1,
                                fields: [
                                    {
                                        label: __('Email Subject'),
                                        fieldname: 'email_subject',
                                        fieldtype: 'Data',
                                        reqd: 1,
										in_list_view:1,
										read_only: 1
                                    },
                                    {
                                        label: __('Email Description'),
                                        fieldname: 'description',
                                        fieldtype: 'Text Editor',
                                        reqd: 1,
										in_list_view:1,
										read_only: 1
                                    },
                                    {
                                        label: __('Name'),
                                        fieldname: 'name',
                                        fieldtype: 'Data',
                                        hidden: 1
                                    }
                                ],
                                data: data_x,
								cannot_add_rows: true,
								cannot_delete_rows: true
                            }
        
                        ],
                        
                        size: 'large', // small, large, extra-large 
                        primary_action_label: 'Send',
                        primary_action(values) {
							let dfh=[]
							
                            
							values.assests.forEach(k => {
                            if(k.__checked==1){
								
									dfh.push(k.name)
	
								
							}
							})
							if(dfh.length==0){
								frappe.msgprint(__("Please Select One Element in Dialog for send mail"));

							}
							var me = this;
							return cur_frm.call({
								method:"b2b_marketing.b2b_marketing.doctype.call.call.send_assets",
								args:{
										doc_name :cur_frm.doc.name,
										assest:dfh
										
									},
								callback: function(r)
									{
										if(r.message)
										console.log("r.message0---------------------",r.message)
										{
											$.each(r.message, function(i, m) {
												console.log("%%%%%%%%%%%%%%",m)
											frappe.call({
												method:"frappe.core.doctype.communication.email.make",
												args: {
													recipients: m.recipients,
													subject: m.subject,
													content: m.content,
													doctype: "Call",
													name: cur_frm.doc.name,
													send_email: 1,
													sender: m.sender,
													sender_full_name: m.sender_name,
													email_template: m.email_template,
													attachments: m.attachment,
												},
												callback: function(r) {
													if(!r.exc) {
														frappe.utils.play_sound("email");
						
														if(m["emails_not_sent_to"]) {
															frappe.msgprint(__("Email not sent to {0} (unsubscribed / disabled)",
																[ frappe.utils.escape_html(m["emails_not_sent_to"]) ]) );
														}
						
														if ((frappe.last_edited_communication[me.doc] || {})[me.key]) {
															delete frappe.last_edited_communication[me.doc][me.key];
														}
														if (cur_frm) {
															// clear input
															cur_frm.timeline.input && cur_frm.timeline.input.val("");
															cur_frm.reload_doc();
														}
						
														// try the success callback if it exists
														if (me.success) {
															try {
						
																me.success(r);
															} catch (e) {
																console.log(e);
															}
														}
						
													}
													else {
														frappe.msgprint(__("There were errors while sending email. Please try again."));
						
														// try the error callback if it exists
														if (me.error) {
															try {
																me.error(r);
															} catch (e) {
																console.log(e);
															}
														}
													}
												}
											});
										})
										}
									}
							})
                  
							d.hide();
                        }
						
						
                    });
					
					cur_frm.call({
						method:"b2b_marketing.b2b_marketing.doctype.call.call.get_assest_data",
						args:{
								doc_name :cur_frm.doc.name
							},
						callback: function(r)
						{
							r.message.forEach(k => {
								d.fields_dict.assests.df.data.push({
									"email_subject": k.email_subject,
									"description":k.description,
									"name": k.name
									
								});
							})
							data_x = d.fields_dict.assests.df.data;
							console.log("&&&&&&&&&&&&",data_x[0])
							d.fields_dict.assests.grid.refresh();
						}
					})
					
				
					d.show();
				

}
cur_frm.cscript.send_mail =function(){

    var me = this;
    return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.send_email",
        args:{
                doc_name :cur_frm.doc.name
            },
        callback: function(r)
           {
                if(r.message)
				console.log("r.message0---------------------",r.message)
                {

                    return frappe.call({
                        method:"frappe.core.doctype.communication.email.make",
                        args: {
                            recipients: r.message.recipients,
                            subject: r.message.subject,
                            content: r.message.content,
                            doctype: "Call",
                            name: cur_frm.doc.name,
                            send_email: 1,
                            sender: r.message.sender,
                            sender_full_name: r.message.sender_name,
                            email_template: r.message.email_template,
                            attachments: r.message.attachment,
                        },
                        callback: function(r) {
                            if(!r.exc) {
                                frappe.utils.play_sound("email");

                                if(r.message["emails_not_sent_to"]) {
                                    frappe.msgprint(__("Email not sent to {0} (unsubscribed / disabled)",
                                        [ frappe.utils.escape_html(r.message["emails_not_sent_to"]) ]) );
                                }

                                if ((frappe.last_edited_communication[me.doc] || {})[me.key]) {
                                    delete frappe.last_edited_communication[me.doc][me.key];
                                }
                                if (cur_frm) {
                                    // clear input
                                    cur_frm.timeline.input && cur_frm.timeline.input.val("");
                                    cur_frm.reload_doc();
                                }

                                // try the success callback if it exists
                                if (me.success) {
                                    try {
//                                        frappe.msgprint(__("Assets Send")),
                                        me.success(r);
                                    } catch (e) {
                                        console.log(e);
                                    }
                                }

                            }
                            else {
                                frappe.msgprint(__("There were errors while sending email. Please try again."));

                                // try the error callback if it exists
                                if (me.error) {
                                    try {
                                        me.error(r);
                                    } catch (e) {
                                        console.log(e);
                                    }
                                }
                            }
                        }
                    });
                }
           }
    });
}
cur_frm.cscript.make_call =function(){
    return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.select_call",
        args:{
                doc_name :cur_frm.doc.contact
            },
        callback: function(r)
            {
             var d = new frappe.ui.Dialog({
    			title: __('Select Number'),
                fields: r.message
            });
            d.fields_dict.call.$input.click(function()
            {
                if(d.fields_dict.phone_number.value == null)
                {
                    frappe.throw(__("Please select number"))
                }
                else
                {
                    d.hide();
                    return cur_frm.call({
                        method:"b2b_marketing.b2b_marketing.doctype.call.call.make_call",
                        freeze: true,
                        freeze_message: __('Calling................'),
                        args:{
                                doc_name :cur_frm.doc.name,
                                dest_number : d.fields_dict.phone_number.value
                            }
                    });
                }
            });
		    d.show();
          }
    });
}

var onload_script = function(frm) {
	frappe.provide('frappe.phone_call');
	frappe.provide('frappe.twilio_conn_dialog_map')
	let device;

	if (frappe.boot.twilio_enabled){
		frappe.run_serially([
			() => setup_device(cur_frm.doc.name),
			() => dialer_screen()
		]);
	}

	function setup_device(name) {
		frappe.call( {
			method: "twilio_integration.twilio_integration.api.generate_access_token",
			callback: (data) => {
				device = new Twilio.Device(data.message.token, {
					codecPreferences: ["opus", "pcmu"],
					fakeLocalDTMF: true,
					enableRingingState: true,
				});

				device.on("ready", function (device) {
					Object.values(frappe.twilio_conn_dialog_map).forEach(function(popup){
						popup.set_header('available');
					})
				});

				device.on("error", function (error) {
					Object.values(frappe.twilio_conn_dialog_map).forEach(function(popup){
						popup.set_header('Failed');
					})
					device.disconnectAll();
					console.log("Twilio Device Error:" + error.message);
				});

				device.on("disconnect", function (conn) {
					update_call_log(conn,name);
					const popup = frappe.twilio_conn_dialog_map[conn];
					// Reomove the connection from map object
					delete frappe.twilio_conn_dialog_map[conn]
					popup.dialog.enable_primary_action();
					popup.show_close_button();
					window.onbeforeunload = null;
					popup.set_header("available");
					popup.hide_mute_button();
					popup.hide_hangup_button();
					popup.hide_dial_icon();
					popup.hide_dialpad();
					// Make sure that dialog is closed when incoming call is disconnected.
					if (conn.direction == 'INCOMING'){
						popup.close();
					}
				});

				device.on("cancel", function () {
					Object.values(frappe.twilio_conn_dialog_map).forEach(function(popup){
						popup.close();
					})
				});

				device.on("connect", function (conn) {
					const popup = frappe.twilio_conn_dialog_map[conn];
					popup.setup_mute_button(conn);
					popup.dialog.set_secondary_action_label("Hang Up")
					popup.set_header("in-progress");
					window.onbeforeunload = function() {
						return "you can not refresh the page";
					}
					popup.setup_dial_icon();
					popup.setup_dialpad(conn);
					document.onkeydown = (e) => {
						let key = e.key;
						if (conn.status() == 'open' && ["0","1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "#", "w"].includes(key)) {
							conn.sendDigits(key);
							popup.update_dialpad_input(key);
						}
					};
				});

				device.on("incoming", function (conn) {
					console.log("Incoming connection from " + conn.parameters.From);
					call_screen(conn);
				});

			}
		});
	}

	function dialer_screen() {
		frappe.phone_call.handler = (to_number, frm) => {
			let to_numbers;
			let outgoing_call_popup;

			if (Array.isArray(to_number)) {
				to_numbers = to_number;
			} else {
				to_numbers = to_number.split('\n');
			}
			outgoing_call_popup = new OutgoingCallPopup(device, to_numbers);
			outgoing_call_popup.show();
		}
	}

	function update_call_log(conn,call_name,status="Completed") {
		if (!conn.parameters.CallSid) return
		frappe.call({
			"method": "twilio_integration.twilio_integration.api.update_call_log",
			"args": {
				"call_sid": conn.parameters.CallSid,
				"call_name":call_name,
				"status": status	
			}
		})
	}

	function call_screen(conn) {
		frappe.call({
			type: "GET",
			method: "twilio_integration.twilio_integration.api.get_contact_details",
			args: {
				'phone': conn.parameters.From
			},
			callback: (data) => {
				let incoming_call_popup = new IncomingCallPopup(device, conn);
				incoming_call_popup.show(data.message);
			}
		});
	}
}

function get_status_indicator(status) {
	const indicator_map = {
		'available': 'blue',
		'completed': 'blue',
		'failed': 'red',
		'busy': 'yellow',
		'no-answer': 'orange',
		'queued': 'orange',
		'ringing': 'green blink',
		'in-progress': 'green blink'
	};
	const indicator_class = `indicator ${indicator_map[status] || 'blue blink'}`;
	return indicator_class;
}

class TwilioCallPopup {
	constructor(twilio_device) {
		this.twilio_device = twilio_device;
	}

	hide_hangup_button() {
		this.dialog.get_secondary_btn().addClass('hide');
	}

	set_header(status) {
		if (!this.dialog){
			return;
		}
		this.dialog.set_title(frappe.model.unscrub(status));
		const indicator_class = get_status_indicator(status);
		this.dialog.header.find('.indicator').attr('class', `indicator ${indicator_class}`);
	}

	setup_mute_button(twilio_conn) {
		let me = this;
		let mute_button = me.dialog.custom_actions.find('.btn-mute');
		mute_button.removeClass('hide');
		mute_button.on('click', function (event) {
			if ($(this).text().trim() == 'Mute') {
				twilio_conn.mute(true);
				$(this).html('Unmute');
			}
			else {
				twilio_conn.mute(false);
				$(this).html('Mute');
			}
		});
	}

	hide_mute_button() {
		let mute_button = this.dialog.custom_actions.find('.btn-mute');
		mute_button.addClass('hide');
	}

	show_close_button() {
		this.dialog.get_close_btn().show();
	}

	close() {
		this.dialog.cancel();
	}

	setup_dialpad(conn) {
		let me = this;
		this.dialpad = new DialPad({
			twilio_device: this.twilio_device,
			wrapper: me.dialog.$wrapper.find('.dialpad-section'),
			events: {
				dialpad_event: function($btn) {
					const button_value = $btn.attr('data-button-value');
					conn.sendDigits(button_value);
					me.update_dialpad_input(button_value);
				}
			},
			cols: 5,
			keys: [
				[ 1, 2, 3 ],
				[ 4, 5, 6 ],
				[ 7, 8, 9 ],
				[ '*', 0, '#' ]
			]
		})
	}

	update_dialpad_input(key) {
		let dialpad_input = this.dialog.$wrapper.find('.dialpad-input')[0];
		dialpad_input.value += key;
	}

	setup_dial_icon() {
		let me = this;
		let dialpad_icon = this.dialog.$wrapper.find('.dialpad-icon');
		dialpad_icon.removeClass('hide');
		dialpad_icon.on('click', function (event) {
			let dialpad_section = me.dialog.$wrapper.find('.dialpad-section');
			if(dialpad_section.hasClass('hide')) {
				me.show_dialpad();
			}
			else {
				me.hide_dialpad();
			}
		});
	}

	hide_dial_icon() {
		let dial_icon = this.dialog.$wrapper.find('.dialpad-icon');
		dial_icon.addClass('hide');
	}

	show_dialpad() {
		let dialpad_section = this.dialog.$wrapper.find('.dialpad-section');
		dialpad_section.removeClass('hide');
	}

	hide_dialpad() {
		let dialpad_section = this.dialog.$wrapper.find('.dialpad-section');
		dialpad_section.addClass('hide');
	}
}

class OutgoingCallPopup extends TwilioCallPopup {
	constructor(twilio_device, phone_numbers) {
		super(twilio_device);
		this.phone_numbers = phone_numbers;
	}

	show() {
		this.dialog = new frappe.ui.Dialog({
			static: 1,
			minimizable: true,
			title: __('Make a Call'),

			
			fields: [
				{
					'fieldname': 'to_number',
					'label': 'To Number',
					'fieldtype': 'Data',
					'ignore_validation': true,
					'options': this.phone_numbers,
					'default': this.phone_numbers[0],
					'read_only': 0,
					'reqd': 1
				}
			],
			primary_action: () => {
			    frappe.run_serially([
			        () => cur_frm.cscript.change_status_start(),
                    // () => cur_frm.cscript.publish_form(),
                    () => {
                        try{
                            this.dialog.disable_primary_action();
                            var params = {
                                To: this.dialog.get_value('to_number')
                            };
                            if (this.twilio_device) {
                                let me = this;
                                let outgoingConnection = this.twilio_device.connect(params);
                                frappe.twilio_conn_dialog_map[outgoingConnection] = this;
                                outgoingConnection.on("ringing", function () {
                                    me.set_header('ringing');
                                });
                            } else {
                                this.dialog.enable_primary_action();
                            }
                        }catch{
                            cur_frm.cscript.change_status_schedule()
                        }
                    }
                ]);
			},
			primary_action_label: __('Call'),
			secondary_action: () => {
				if (this.twilio_device) {
					this.twilio_device.disconnectAll();
				}
			},
			onhide: () => {
				if (this.twilio_device) {
					this.twilio_device.disconnectAll();
				}
			}
		});
		let to_number = this.dialog.$wrapper.find('[data-fieldname="to_number"]').find('[type="text"]');

		$(`<span class="dialpad-icon hide">
			<a class="btn-open no-decoration" title="${__('Dialpad')}">
				${frappe.utils.icon('dialpad')}
		</span>`).insertAfter(to_number);

		$(`<div class="dialpad-section hide"></div>`)
		.insertAfter(this.dialog.$wrapper.find('.modal-content'));

		this.dialog.add_custom_action('Mute', null, 'btn-mute mr-2 hide');
		this.dialog.get_secondary_btn().addClass('hide');
		this.dialog.show();
		this.dialog.get_close_btn().show();
		this.dialog.get_close_btn().on('click', () => {
		    console.log("-------cur_frm.doc.start_call",cur_frm.doc.start_call)
		    if(cur_frm.doc.start_call == 1){
		        cur_frm.cscript.change_status_complete()
		    }
		});
	}
}

class IncomingCallPopup extends TwilioCallPopup {
	constructor(twilio_device, conn) {
		super(twilio_device);
		this.conn = conn;
		frappe.twilio_conn_dialog_map[conn] = this; // CHECK: Is this the place?
	}

	get_title(caller_details) {
		let title;
		if (caller_details){
			title = __('Incoming Call From {0}', [caller_details.first_name]);
		} else {
			title = __('Incoming Call From {0}', [this.conn.parameters.From]);
		}
		return title;
	}

	set_dialog_body(caller_details) {
		var caller_info = $(`<div></div>`);
		let caller_details_html = '';
		if (caller_details) {
			for (const [key, value] of Object.entries(caller_details)) {
				caller_details_html += `<div>${key}: ${value}</div>`;
			}
		} else {
			caller_details_html += `<div>Phone Number: ${this.conn.parameters.From}</div>`;
		}
		$(`<div>${caller_details_html}</div>`).appendTo(this.dialog.modal_body);
	}

	show(caller_details) {
		this.dialog = new frappe.ui.Dialog({
			'static': 1,
			'title': this.get_title(caller_details),
			'minimizable': true,
			primary_action: () => {
				this.dialog.disable_primary_action();
				this.conn.accept();
			},
			primary_action_label: __('Answer'),
			secondary_action: () => {
				if (this.twilio_device) {
					if (this.conn.status() == 'pending') {
						this.conn.reject();
						this.close();
					}
					this.twilio_device.disconnectAll();
				}
			},
			secondary_action_label: __('Hang Up'),
			onhide: () => {
				if (this.twilio_device) {
					if (this.conn.status() == 'pending') {
						this.conn.reject();
						this.close();
					}
					this.twilio_device.disconnectAll();
				}
			}
		});
		this.set_dialog_body(caller_details);
		this.show_close_button();
		this.dialog.add_custom_action('Mute', null, 'btn-mute hide');
		this.dialog.show();
	}
}

class DialPad extends OutgoingCallPopup {
	constructor({ twilio_device, wrapper, events, cols, keys, css_classes, fieldnames_map }) {
		super(twilio_device);
		this.wrapper = wrapper;
		this.events = events;
		this.cols = cols;
		this.keys = keys;
		this.css_classes = css_classes || [];
		this.fieldnames = fieldnames_map || {};

		this.init_component();
	}

	init_component() {
		this.prepare_dom();
		this.bind_events();
	}

	prepare_dom() {
		const { cols, keys, css_classes, fieldnames } = this;

		function get_keys() {
			return keys.reduce((a, row, i) => {
				return a + row.reduce((a2, number, j) => {
					const class_to_append = css_classes && css_classes[i] ? css_classes[i][j] : '';
					const fieldname = fieldnames && fieldnames[number] ?
						fieldnames[number] : typeof number === 'string' ? frappe.scrub(number) : number;

					return a2 + `<div class="dialpad-btn ${class_to_append}" data-button-value="${fieldname}">${number}</div>`;
				}, '');
			}, '');
		}

		this.wrapper.html(
			`<i class="dialpad--pointer"></i>
			<div class="dialpad-container">
				<input class="dialpad-input form-control" readonly="true">
				<div class="dialpad-keys">
					${get_keys()}
				</div>
			</div>`
		)
	}

	bind_events() {
		const me = this;
		this.wrapper.on('click', '.dialpad-btn', function() {
			const $btn = $(this);
			me.events.dialpad_event($btn);
		});
	}
}

var script = document.createElement('script');
document.head.appendChild(script);
script.onload = onload_script;
script.src = "https://sdk.twilio.com/js/client/releases/1.13.0/twilio.min.js";
