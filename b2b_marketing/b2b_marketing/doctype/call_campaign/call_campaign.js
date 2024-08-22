// Copyright (c) 2021, Dexciss and contributors
// For license information, please see license.txt

frappe.provide('frappe.phone_call');
frappe.provide('frappe.twilio_conn_dialog_map')
let device;
let id;
frappe.ui.form.on('Call Campaign', {
    onload:(frm) => {
        frappe.run_serially([
            () =>frm.set_value("current_status","Offline"),
            () =>frm.refresh_field("current_status"),
            () =>frm.refresh_field("status"),
            () => frm.clear_table("start_campaign_call_list"),
            () => frm.set_value("current_status","Offline"),
            () => frm.set_value("call",""),
            // () =>frm.set_value("select_campaign",""),
            () =>frm.set_value("campaign",""),
            () => frm.set_df_property("qsession_start","hidden",1),
            () => frm.set_df_property("check_in","hidden",1),
            () => frm.trigger("clear_field"),
            () =>frm.set_df_property("script_section","hidden",1),
            () => {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Agents",
                        name: frm.doc.agent,
                        fieldname: "status",
                        value: frm.doc.current_status,
                    },
                    callback: function(r) { }
                });
            },
            () =>{
                if(frm.doc.agent){
                    frappe.call({
                        method: "b2b_marketing.b2b_marketing.doctype.call_campaign.call_campaign.filtered_campaigns",
                        args: {
                            agent: frm.doc.agent,
                        },
                        callback: function(r) {
                            if(r.message){
                                frm.set_df_property('select_campaign','options',r.message)
                                frm.refresh_field("select_campaign")
                            }
                         }
                    });
                }
                

            }
            // () => frm.save(),
        ]);
        cur_frm.trigger('refresh')
                
    },
    setup: function (frm) {
        frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 'name', (r) => {
            if (r && r.name) {
                frappe.db.get_value('Agents', {'employee': r.name}, 'name', (k) => {
                    if (k && k.name) 
                        {
                        frm.set_value("agent",k.name);
                        frm.refresh_field("agent")
                        // frm.save()
                    }
                    else
                    {
                        frm.trigger('clear_field');
                        frappe.msgprint(__("Kindly ensure that the Employee is properly linked or assigned to the agent."));
                    }
                });
            }else{
                frm.trigger('clear_field');
                // frm.save()
                frappe.msgprint(__("Please ensure that the user is properly allocated to the employee."));
            }
        });
    },
    make_dashboard: function(frm) {
        if(frm.doc.__islocal)
            return;
        frm.dashboard.refresh();
        const timer = `
            <div class="stopwatch" style="font-weight:bold;margin:0px 13px 0px 2px;
                color:#545454;font-size:18px;display:inline-block;vertical-align:text-bottom;>
                <span class="hours">00</span>
                <span class="colon">:</span>
                <span class="minutes">00</span>
                <span class="colon">:</span>
                <span class="seconds">00</span>
            </div>`;
        var section = frm.toolbar.page.add_inner_message(timer);

        let currentIncrement = frm.doc.current_time || 0;
            function initialiseTimer() {
                const interval = setInterval(function() {
                    var current = setCurrentIncrement();
                    updateStopwatch(current);
                }, 1000);
            }
            function updateStopwatch(increment) {
                var hours = Math.floor(increment / 3600);
                var minutes = Math.floor((increment - (hours * 3600)) / 60);
                var seconds = increment - (hours * 3600) - (minutes * 60);

                $(section).find(".hours").text(hours < 10 ? ("0" + hours.toString()) : hours.toString());
                $(section).find(".minutes").text(minutes < 10 ? ("0" + minutes.toString()) : minutes.toString());
                $(section).find(".seconds").text(seconds < 10 ? ("0" + seconds.toString()) : seconds.toString());
            }

            function setCurrentIncrement() {
                currentIncrement += 1;
                return currentIncrement;
            }
    },
    select_campaign:(frm) =>{
        if(frm.doc.select_campaign){
            frm.set_df_property("check_in",'hidden',0)
            frm.set_value("campaign",frm.doc.select_campaign)
            frm.refresh_field("campaign")
            if(frm.doc.campaign){
                frm.call({
                    doc: frm.doc,
                    freeze: true,
                    method: "check_scheduled_call",
                    callback: (r) => {
                        if(r.message){
                            frm.set_df_property('check_in','hidden',1)
                        }
                    }
                });
            }
            if(frm.doc.campaign){
                frappe.db.get_doc("Campaigns",frm.doc.campaign).then(cam => {
                    if(cam.script)
                    {
                        $(frm.fields_dict['script'].wrapper).html(cam.script);
                        frm.refresh_field("script")
                    }
                    else
                    {
                        $(frm.fields_dict['script'].wrapper).html("");
                        frm.refresh_field("script")
                        frm.set_df_property("script_section","hidden",1)
                    }
                })
            }
        }
    },
    refresh:(frm) =>{
        frm.disable_save()
        if(cur_frm.doc.current_status == "Offline")
        {
            frm.set_value("call","");
            frm.refresh_field("call")
            frm.set_df_property("qsession_start","hidden",1)
            frm.set_df_property("qsession_end","hidden",1)
            if(!frm.doc.select_campaign && !frm.doc.campaign)
            {
                frm.set_df_property('check_in','hidden',1)
            }
        }
        if(cur_frm.doc.current_status == "Online"){
            if (frm.doc.campaign) {
                frappe.db.get_value('Campaigns', {'name': frm.doc.campaign}, 'campaigns_name')
                    .then(r => {
                        if (r.message && r.message.campaigns_name) {
                            let campaign_name = r.message.campaigns_name;
                            frappe.db.get_value('Campaigns Designer', {'name': campaign_name}, 'auto_send_email')
                                .then(res => {
                                    if (res.message.auto_send_email==0) {
                                        frm.add_custom_button('Send Template Email', function() {
                                            cur_frm.cscript.send_mail()
                                        })
                                    }
                                });
                        }
                    });
            }
        
        frm.add_custom_button('Send Assets', function() {
            cur_frm.cscript.send_assets()
        });
        frm.add_custom_button(__("Edit Contact/Organization"), function () {
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
                        {fieldtype:"Column Break"},
                        {
                            label: 'Title',
                            fieldname: 'title',
                            fieldtype: 'Link',
                            options:"Title"
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
                            fieldtype: 'Data'
                        },
                        {fieldtype:"Column Break"},
                        {
                            label: 'Domain',
                            fieldname: 'domain',
                            fieldtype: 'Data'
                        },
                    ],
                    primary_action_label: 'Update',
                    primary_action(values) {
                        frappe.call({
                            method:"b2b_marketing.b2b_marketing.doctype.call.call.update_callcamp_ct_org",
                            args:{
                                "contact":frm.doc.contact,
                                "organization":frm.doc.organization,
                                "values":values,
                                "doc_id":frm.doc.call
                            },
                            callback: (r) => {
                                if(r.message){
                                    for (var i = 0; i < r.message.length; i++) {
                                        var val = r.message[i];
                                        var key = Object.keys(val)[0];
                                        var value = val[key];
                                        frm.set_value(key,value)
                                    }
                                    frm.save()
                                }
                            }
                        })
                        d.hide();
                    }
                });
                d.show();
            })
        }
        if(cur_frm.doc.current_status == "Online"){
                var msg = "Would you like to proceed to the next call or skip this one?";
                frm.add_custom_button(__("Next"), function () {
                    frappe.confirm(
                        msg,
                        function() {
                            if(frm.doc.call){
                                let each_flag=false
                                cur_frm.set_value("call_start",0);
                                $.each(frm.doc.start_campaign_call_list, function(i, m) {
                                    if(m.call == frm.doc.call){
                                        m.next_call = 1
                                    }
                                });
                                $.each(frm.doc.start_campaign_call_list, function(i, m) {
                                    
                                    if(m.next_call == 0){
                                        if (each_flag==true){
                                        return false
                                        }
                                        frm.trigger('clear_field');
                                        frm.set_value('call',m.call);
                                        
                                        frappe.call({
                                            method:"get_call_self",
                                            doc:frm.doc,
                                            frezee:true,
                                            async: false,
                                            freeze_message:"Fetching Contact",
                                            args:{
                                                "call":m.call
                                            
                                            },
                                            callback:(r) => {
                                                if(r.message){
                                                    frappe.db.get_value('Call', {'name': frm.doc.call}, 
                                                    ['mobile_phone', 'phone', 'organization_phone', 'corporate_phone'], 
                                                    function(k) {
                                                        if (!k.exc) {
                                                            
                                                            frm.set_value("mobile_phone", k.mobile_phone);
                                                            frm.set_value("phone", k.phone);
                                                            frm.set_value("organization_phone", k.organization_phone);
                                                            frm.set_value("corporate_phone", k.corporate_phone);
                                                            frm.refresh_field("mobile_phone")
                                                            frm.refresh_field("phone")
                                                            frm.refresh_field("organization_phone")
                                                            frm.refresh_field("corporate_phone")
                                                        }
                                                    });
                                                    each_flag=true
                                                    return false
                                                }
                                            }
                                            })
                                        
                                    }
                                  
                                });
                            }
                        }
                    );
                }).addClass("btn-primary");
        }
    },
    select_to_dial:(frm) =>{
        var std = frm.doc.select_to_dial.split(" ")
        frm.set_value("phone",std[0])
        frm.save()
    },
    check_in: (frm) => {
		frappe.run_serially([
			// Set the agent's current status to "Online"
			() => frm.set_value("current_status", "Online"),
	
			// Refresh the "current_status" field to reflect the new value
			() => frm.refresh_field("current_status"),
	
			// Create an agent log for "Check In"
			() => cur_frm.cscript.create_agent_log("Check In"),
	
			// Show the script section
			() => frm.set_df_property("script_section", "hidden", 0),
	
			// Verify that the user is linked to an employee and an agent
			() => {
				frappe.db.get_value('Employee', {'user_id': frappe.session.user}, 'name', (r) => {
					if (r && r.name) {
						frappe.db.get_value('Agents', {'employee': r.name}, 'name', (k) => {
							if (k && k.name) {
								console.log("ok");
							} else {
								frm.trigger('clear_field');
								frappe.msgprint(__("Kindly ensure that the Employee is properly linked or assigned to the agent."));
							}
						});
					} else {
						frm.trigger('clear_field');
						frappe.msgprint(__("Please ensure that the User is properly allocated to the Employee."));
					}
				});
			},
	
			// Clear the "start_campaign_call_list" table
			() => frm.clear_table("start_campaign_call_list"),
	
			// Set the agent's current status to "Online" again (redundant but might be necessary)
			() => frm.set_value("current_status", "Online"),
	
			// Update the agent's status in the database
			() => {
				frappe.call({
					method: "frappe.client.set_value",
					args: {
						doctype: "Agents",
						name: frm.doc.agent,
						fieldname: "status",
						value: frm.doc.current_status,
					},
					callback: function(r) { }
				});
			},
            
			() => {
				 frm.call({
					doc: frm.doc,
					freeze: true,
					method: "get_call",
					freeze_message: __("Getting All Available Call..."),
					 callback: async (r) => {
                        id=0
						if (!r.exc && r.message) {
							for (var data in r.message) {
								if (!frm.doc.call) {
									var d = frm.add_child("start_campaign_call_list");
									d.call = r.message[data];
								}
							}
							frm.refresh_field('start_campaign_call_list');
	
							// Iterate through calls and fetch details for the first available one
						for (var data in r.message) {
								if (!frm.doc.call || id==0) {
									await frappe.call({
										method: "get_call_self",
										doc: frm.doc,
										args: {
											"call": r.message[data]
										},
										callback: (res) => {
											if (res.message) {
												id=1
												frm.set_value("call", r.message[data]);
                                                frm.refresh_field("call")
												// Fetch call details and set form values
												frappe.db.get_value('Call', {'name': r.message[data]}, 
													['mobile_phone', 'phone', 'organization_phone', 'corporate_phone'], 
													function(k) {
															frm.set_value("mobile_phone", k.mobile_phone);
															frm.set_value("phone", k.phone);
															frm.set_value("organization_phone", k.organization_phone);
															frm.set_value("corporate_phone", k.corporate_phone);
															frm.refresh_field("mobile_phone");
															frm.refresh_field("phone");
															frm.refresh_field("organization_phone");
															frm.refresh_field("corporate_phone");
															frm.trigger('refresh');
														
													});
												data.next_call = 1;
												id=1
												return false
												
											}
											

										}
									});
								}
								// if (id==1){
								// 	break;
								// }
							}
						}
					}
				});
			},
	
			// Show additional fields related to session start and campaign selection
			() => frm.set_df_property("qsession_start", "hidden", 0),
			() => frm.set_df_property("select_campaign", "hidden", 0),
	
			// Refresh the form
			() => frm.trigger('refresh'),
	
			// Show the agent field
			() => frm.set_df_property("agent", "hidden", 0),
	
			// Display a success alert
			() => frappe.show_alert('Agent Login Successfully.', 8)
		]);
	},
	
	

    check_out:(frm) =>{
        frappe.run_serially([
            () =>frm.set_value("current_status","Offline"),
            () =>frm.refresh_field("current_status"),
            () =>frm.refresh_field("status"),
            () => frm.clear_table("start_campaign_call_list"),
            () => frm.set_value("current_status","Offline"),
            () => frm.set_value("call",""),
            () => cur_frm.cscript.create_agent_log("Check Out"),
            () =>frm.set_value("select_campaign",""),
            () =>frm.refresh_field("select_campaign"),
            () =>frm.set_value("campaign",""),
            () => frm.set_df_property("qsession_start","hidden",1),
            () => frm.set_df_property("check_in","hidden",1),
            () => frm.trigger("clear_field"),
            () =>frm.set_df_property("script_section","hidden",1),
            () => {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Agents",
                        name: frm.doc.agent,
                        fieldname: "status",
                        value: frm.doc.current_status,
                    },
                    callback: function(r) { }
                });
            },
            // () => frm.save(),
            ()=>frappe.show_alert('Agent Logout Successfully.', 8)
        ]);
        cur_frm.trigger('refresh')
    },

    break_start:(frm) =>{
        frappe.run_serially([
            () => frm.set_value("current_status","On Break"),
            () => cur_frm.cscript.create_agent_log("Break Start"),
            () => frm.set_df_property("select_campaign","hidden",1),
            () => frm.set_df_property("campaign","hidden",1),
            () => frm.set_df_property("qsession_start","hidden",1),
            () => frm.set_df_property("script_section","hidden",1),
            () => frm.set_df_property("check_out","hidden",1),
            () => {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Agents",
                        name: frm.doc.agent,
                        fieldname: "status",
                        value: frm.doc.current_status,
                    },
                    callback: function(r) { }
                });
            },
            // () => frm.save()
        ]);
    },

    break_end:(frm) =>{
        frappe.run_serially([
            () => frm.set_value("current_status","Online"),
            () => cur_frm.cscript.create_agent_log("Break End"),
            () => frm.set_df_property("select_campaign","hidden",0),
            () => frm.set_df_property("campaign","hidden",0),
            () => frm.set_df_property("agent","hidden",0),
            () => frm.set_df_property("qsession_start","hidden",0),
            () => frm.set_df_property("script_section","hidden",0),
            () => frm.set_df_property("check_out","hidden",0),
            () => {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Agents",
                        name: frm.doc.agent,
                        fieldname: "status",
                        value: frm.doc.current_status,
                    },
                    callback: function(r) { }
                });
            },
            // () => frm.save()
        ]);
    },

    qsession_start:(frm) =>{
        frappe.run_serially([
            () => frm.set_df_property("qsession_end","hidden",0),
            () => frm.set_value("current_status","Quality Session"),
            () => cur_frm.cscript.create_agent_log("Quality Session Start"),
            () => frm.set_df_property("qsession_start","hidden",1),
            () => frm.set_df_property("select_campaign","hidden",1),
            () => frm.set_df_property("campaign","hidden",1),
            () => frm.set_df_property("script_section","hidden",1),
            () => {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Agents",
                        name: frm.doc.agent,
                        fieldname: "status",
                        value: frm.doc.current_status,
                    },
                    callback: function(r) { }
                });
            },
            // () => frm.save(),
            
        ]);
    },

    qsession_end:(frm) =>{
        frappe.run_serially([
            () => frm.set_value("current_status","Online"),
            () => cur_frm.cscript.create_agent_log("Quality Session End"),
            () => frm.set_df_property("qsession_end","hidden",1),
            () => frm.set_df_property("qsession_start","hidden",0),
            () => frm.set_df_property("select_campaign","hidden",0),
            () => frm.set_df_property("campaign","hidden",0),
            () => frm.set_df_property("script_section","hidden",0),
            () => {
                frappe.call({
                    method: "frappe.client.set_value",
                    args: {
                        doctype: "Agents",
                        name: frm.doc.agent,
                        fieldname: "status",
                        value: frm.doc.current_status,
                    },
                    callback: function(r) { }
                });
            },
            // () => frm.save()
        ]);
    },
    clear_field:(frm) =>{
         frm.set_value("organization", "");
         frm.set_value('scheduled_queue', "");
         frm.set_value('status', "");
         frm.set_value('start_time', "");
         frm.set_value('end_time', "");
         frm.set_value('disposal', "");
         frm.set_value("organization_limit_reach", "");
         frm.set_value("daily_limit_reach", "");
         frm.set_value("contact","")
         frm.set_value("organization","")
         frm.set_value("phone","")
         frm.set_value("status","")
         frm.set_value("scheduled_queue","")
         frm.set_value("notes","")
    }
});

cur_frm.cscript.change_status_start= function()
    {
    cur_frm.set_value("call_start",1);
     return cur_frm.call({
         method:"b2b_marketing.b2b_marketing.doctype.call.call.check_limit",
         args: {
                doc: cur_frm.doc
               },
         callback: function(r)
             {
                 if (r.message)
                 {
                    console.log(new Date().getDate())
                    cur_frm.call("change_status_start");
                 }
             }
     });
 };  
 cur_frm.cscript.change_status_schedule= function()
 {
    frappe.db.set_value('Call', cur_frm.doc.call, 'status', "On-going");
    frappe.db.set_value('Call', cur_frm.doc.call, 'start_time', new Date());
 };
cur_frm.cscript.change_status_no_answer= function()
 {
    frappe.db.set_value('Call', cur_frm.doc.call, 'status', "No-Answer");
 };

cur_frm.cscript.change_status_complete= function()
 {

    cur_frm.call('change_status_complete_p');
    var d = new frappe.ui.Dialog({
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
                    "fieldname": "sb1",
                    "fieldtype": "Section Break",
                },
                {
                    "label": 'Select For Break',
                    "fieldname": "break",
                    "fieldtype": "Select",
                    "options":["Continue Campaign","Submit & Start Break","Submit & End Break"]
                }
            ],
        });
        d.get_close_btn().hide();
        d.fields_dict.create_lead.$input.click(function() {
            d.hide();
            frappe.run_serially([
                () => cur_frm.cscript.create_lead(),
                () => cur_frm.cscript.build_invoice(),
                () => cur_frm.call('update_agent_status'),
                // () => cur_frm.save()

            ]);

        });

        d.fields_dict.call_back.$input.click(function() {
            d.hide();
            frappe.run_serially([
                () => frappe.db.set_value('Call', cur_frm.doc.call, 'call_disposal', "Call Back"),
                () => cur_frm.cscript.check_quality_review_in_camp_design("Call Back"),
                () => cur_frm.cscript.build_invoice(),
                () => cur_frm.cscript.create_new_call(),
                () => cur_frm.call('update_agent_status'),
                () => cur_frm.set_value('disposal', "Call Back"),
                () => cur_frm.refresh_field('disposal')
                // () => cur_frm.save()

            ]);


        });

        d.fields_dict.answering_machine_prospect.$input.click(function() {
            d.hide();
            frappe.run_serially([
                () => frappe.db.set_value('Call', cur_frm.doc.call, 'call_disposal', "Answering Machine - Prospect"),
                () => cur_frm.cscript.check_quality_review_in_camp_design("Answering Machine - Prospect"),
                () => cur_frm.cscript.build_invoice(),
                () => cur_frm.call('update_agent_status'),
                () => cur_frm.set_value('disposal', "Answering Machine - Prospect"),
                () => cur_frm.refresh_field('disposal')
                // () => cur_frm.save()

            ]);

        });

        d.fields_dict.answering_machine_operator.$input.click(function() {
            d.hide();
            frappe.run_serially([
                () => frappe.db.set_value('Call', cur_frm.doc.call, 'call_disposal', "Answering Machine - Operator"),
                () => cur_frm.cscript.check_quality_review_in_camp_design("Answering Machine - Operator"),
                () => cur_frm.cscript.build_invoice(),
                () => cur_frm.call('update_agent_status'),
                () => cur_frm.set_value('disposal', "Answering Machine - Operator"),
                () => cur_frm.refresh_field('disposal')
                // () => cur_frm.save()
            ]);

        });

        d.fields_dict.no_answer.$input.click(function() {
            d.hide();
            frappe.run_serially([
            () => frappe.db.set_value('Call', cur_frm.doc.call, 'call_disposal', "No Answer"),
            () => cur_frm.cscript.check_quality_review_in_camp_design("No Answer"),
            () => cur_frm.cscript.change_status_no_answer(),
            () => cur_frm.cscript.build_invoice(),
            () => cur_frm.call('update_agent_status'),
            () => cur_frm.set_value('disposal', "Answering Machine - Operator"),
            () => cur_frm.refresh_field('disposal')
            // () => cur_frm.save()

            ]);

        });

        d.fields_dict.hang_up.$input.click(function() {
            d.hide();
            frappe.run_serially([
            () => frappe.db.set_value('Call', cur_frm.doc.call, 'call_disposal', "Hang up"),
            () => cur_frm.cscript.check_quality_review_in_camp_design("Hang up"),
            () => cur_frm.cscript.build_invoice(),
            () => cur_frm.call('update_agent_status'),
            () => cur_frm.set_value('disposal', "Hang up"),
            () => cur_frm.refresh_field('disposal')
            // () => cur_frm.save()
            ]);

        });

        d.fields_dict.not_interested.$input.click(function() {
            d.hide();
            frappe.run_serially([
                () => frappe.db.set_value('Call', cur_frm.doc.call, 'call_disposal', "Not Interested"),
                () => cur_frm.cscript.check_quality_review_in_camp_design("Not Interested"),
                () => cur_frm.cscript.build_invoice(),
                () => cur_frm.call('update_agent_status'),
                () => cur_frm.set_value('disposal', "Not Interested"),
                () => cur_frm.refresh_field('disposal')
                // () => cur_frm.save()

            ]);

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
                        frappe.db.set_value('Call', cur_frm.doc.call, 'call_disposal', "DNC");
                         cur_frm.cscript.check_quality_review_in_camp_design("DNC");
                         cur_frm.cscript.build_invoice()
                         cur_frm.call('update_agent_status')
                         cur_frm.set_value('disposal', "DNC"),
                         cur_frm.refresh_field('disposal')
                        //  cur_frm.save()

                     }
            });
        });
        d.show();
        d.get_close_btn().on('click', () => {
             frappe.db.get_value(
                    "Call",
                    cur_frm.doc.call,
                    "status",
                    (r) => {
                        if(r.status == "On-going"){
                            frappe.db.set_value('Call', cur_frm.doc.call, 'status', "Scheduled");
                            // cur_frm.save()
                        }else{
                            frappe.db.set_value('Call', cur_frm.doc.call, 'status', "On-going");
                            // cur_frm.save()
                        }
                    }
                );
        });

 };
cur_frm.cscript.create_lead = function()
 {
    return cur_frm.call({
         method:"b2b_marketing.b2b_marketing.doctype.call.call.create_lead",
         args: {
                doc: cur_frm.doc.call
               },
         callback: function(r)
             {
                 if (r.message)
                 {
//                     cur_frm.reload_doc();
                 }
             }
    });
 };
 cur_frm.cscript.build_invoice = function(){
    return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.build_invoice",
        args:{
                charge_type: "Charge Per Call",
                doc_name :cur_frm.doc.call,
                doc : "Call",
                voucher : cur_frm.doc.call
           },
        callback: function(r)
           {
           }
     });
}
cur_frm.cscript.check_quality_review_in_camp_design =function(disposal){
     return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.check_quality_review_in_camp_design",
        args:{
                call_disposal: disposal,
                doc_name :cur_frm.doc.call
           },
        callback: function(r)
           {
           }
     });
}
cur_frm.cscript.create_new_call = function(){
    return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.create_new_call",
        args:{
                doc_name :cur_frm.doc.call
            },
        callback: function(r)
           {
           }
    });
}

cur_frm.cscript.create_agent_log= function(status)
    {
    cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call_campaign.call_campaign.create_agent_log",
        args:{
                agent: cur_frm.doc.agent,
                status :status,
                campaign:cur_frm.doc.campaign,
                notes:cur_frm.doc.notes
           },
        callback: function(r)
           {
           }
     });
    };

var onload_script = function() {
    frappe.provide('frappe.phone_call');
    frappe.provide('frappe.twilio_conn_dialog_map')
    let device;

    if (frappe.boot.twilio_enabled){
        frappe.run_serially([
            () => setup_device(),
            () => dialer_screen()
        ]);
    }

    function setup_device() {
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
                    update_call_log(conn);
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
            outgoing_call_popup.show(frm);
        }
    }

    function update_call_log(conn, status="Completed") {
        if (!conn.parameters.CallSid) return
        frappe.call({
            "method": "twilio_integration.twilio_integration.api.update_call_log",
            "args": {
                "call_sid": conn.parameters.CallSid,
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
cur_frm.cscript.send_mail =function(){

    var me = this;
    return cur_frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.call.call.send_email",
        args:{
                doc_name :cur_frm.doc.call
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
                            name: cur_frm.doc.call,
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
                                        doc_name :cur_frm.doc.call,
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
                                                    name: cur_frm.doc.call,
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
                                doc_name :cur_frm.doc.call
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

    show(frm) {
        this.dialog = new frappe.ui.Dialog({
            'static': 1,
            'title': __('Make a Call'),
            'minimizable': true,
            'fields': [
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
                            console.log("Agent When Called",frm.doc.agent)
                            var sec = frm.toolbar.page.inner_toolbar.find(".stopwatch")
                    let currentIncrement = frm.doc.current_time || 0;
                    currentIncrement += moment(frappe.datetime.now_datetime()).diff(moment(frm.doc.started_time),"seconds");
                    initialiseTimer();
                    console.log("sec-----------------",sec)

                    function initialiseTimer() {
                        const interval = setInterval(function() {
                            var current = setCurrentIncrement();
                            updateStopwatch(current);
                        }, 1000);
                    }

                    function updateStopwatch(increment) {
                        var hours = Math.floor(increment / 3600);
                        var minutes = Math.floor((increment - (hours * 3600)) / 60);
                        var seconds = increment - (hours * 3600) - (minutes * 60);
        
                        $(sec).find(".hours").text(hours < 10 ? ("0" + hours.toString()) : hours.toString());
                        $(sec).find(".minutes").text(minutes < 10 ? ("0" + minutes.toString()) : minutes.toString());
                        $(sec).find(".seconds").text(seconds < 10 ? ("0" + seconds.toString()) : seconds.toString());
                    }
        
                    function setCurrentIncrement() {
                        currentIncrement += 1;
                        return currentIncrement;
                    }
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
//          this.dialog.hide()
            if(cur_frm.doc.call_start == 1){
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
            static: 1,
            title: this.get_title(caller_details),
            minimizable: true,
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

