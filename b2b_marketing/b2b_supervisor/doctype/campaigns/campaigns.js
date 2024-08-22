// Copyright (c) 2019, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Campaigns', {
	 refresh: function(frm) {
	    if(!frm.doc.__islocal)
        {
            if(frm.doc.status !== "To Start")
            {
	            if(!frm.is_dirty())
                {
                    cur_frm.set_read_only(true);
	            }
	        }
            if(frm.doc.status == "To Start")
            {
                frm.add_custom_button(__('Start'), function() {
                    if(frm.doc.status != "Running")
                    {
                        cur_frm.cscript.change_status_start()
                        frm.refresh_field('status')

                    }
                });

            }
            if(frm.doc.status == "Running")
            {
                frm.add_custom_button(__('Complete'), function() {
                        cur_frm.cscript.change_status_complete()
                }).addClass('btn-primary');
                frm.add_custom_button(__('Cancel'), function() {
                    frappe.call({
                        method: 'cancel_call_scheduled',
                        doc: frm.doc,
                        freeze: true,
                        freeze_message: "Calls are being cancelled, please wait in some time...",
                        async: true,
                        callback:function(r){
                            window.location.reload()
                        }
                    })
                    // cur_frm.cscript.change_status_cancel()
                });
            }
        }
        if(frm.doc.__onload && frm.doc.__onload.dashboard_info)
        {
			var info = frm.doc.__onload.dashboard_info;
			frm.dashboard.add_indicator(__('Success: {0}',
				[info.lead]), 'blue');                                       //Success (Number of leads submitted)
			frm.dashboard.add_indicator(__('Success Rate: {0}%',
				[info.rate]), 'blue');                                        //Success (Number of leads submitted)
			frm.dashboard.add_indicator(__('Target Shortfall: {0}',
				[info.shortfall]), 'blue');                                      //Success Rate in % (formula = Number of leads submitted / Callable * 100)
		}
        return frm.call('get_online_agent_count'),frm.call('get_callable_contact_count');

	 },
     after_save :function(frm){
        frm.set_value('number_of_agents',frm.doc.agents_list.length)
    },
	 validate :function(frm){
	        return frm.call('get_online_agent_count'),frm.call('get_callable_contact_count');
	 },
	 onload: function(frm){
        frm.set_query('agent_name', function(doc) {
            return {
                filters: {
                    "is_group":1,
                }
            };
        });
    },
    before_save: function(frm){
        if(frm.doc.campaigns_name){
            frappe.db.get_value('Campaigns Designer', {'name': frm.doc.campaigns_name}, 'filter_contact', (r) => {
                if (r && r.filter_contact) {
                    frm.set_value('campaigns_designer_filter',r.filter_contact);
                }

            });
        }
    },
    agent_name: function(frm){
            return frm.call('set_sub_agents').then(() => {
            frm.refresh_field('agents_list');
        });
    },
});
cur_frm.cscript.change_status_start= function()
 {
    frappe.run_serially([
        () => cur_frm.call('create_calls', {
            freeze: true,
            freeze_message: "Calls are being scheduled, please wait in some time...",
            async: true,
        }),
        () => cur_frm.reload_doc()
    ]);
 };

cur_frm.cscript.change_status_complete= function()
 {
    return cur_frm.call({
        method:"b2b_marketing.b2b_supervisor.doctype.campaigns.campaigns.build_invoice",
        args:{
                doc_name :cur_frm.doc.name
           },
        callback: function(r)
           {
                frappe.run_serially([
                    () => cur_frm.set_value('status', "Completed"),
                    () => cur_frm.save()
                ]);
           }
     });
 };
// cur_frm.cscript.change_status_cancel= function()
//  {
//     cur_frm.set_value("status", "Cancelled");
//     cur_frm.save();
//     // window.location.reload()
//  };

cur_frm.cscript.update_contact = function(doc){
    var filter = "";
    frappe.db.get_value('Campaigns Designer', {'name': cur_frm.doc.campaigns_name}, 'filter_contact', (r) => {
            if (r && r.filter_contact) {
                var filter = r.filter_contact
            }
    });
    frappe.call({
            method: 'b2b_marketing.b2b_marketing.doctype.campaigns_designer.campaigns_designer.get_contact_list',
            args: {
                filters:filter,
                self:cur_frm.doc.campaigns_name
            },
            callback: function(r) {
                var arr = r.message;
                if(arr == 1){
                    frappe.validated = false;
                }else{
                    var lst_contact = []
                    var change_status = 0
                    for(var row in cur_frm.doc.contact_list){
                        lst_contact.push(cur_frm.doc.contact_list[row]['contact'])
                    }
                    for(var ele in arr){
                        var valid_cont = lst_contact.includes(arr[ele]['contact'])
                        if(valid_cont != true){
                            change_status = 1
                            cur_frm.set_value('total_available_contacts',arr[ele]['total_available_contacts']);
                            var child = cur_frm.add_child('contact_list')
                            child.contact = arr[ele]['contact']
                            child.organization = arr[ele]['organization']
                            child.phone = arr[ele]['phone']
                            child.mobile = arr[ele]['mobile']
                            child.email = arr[ele]['email']
                        }
                    }
                    if(change_status == 1){
                        cur_frm.set_value("status", "To Start");
                    }
                    cur_frm.refresh_field("contact_list");
                    cur_frm.refresh_field('total_available_contacts')
                }
            }
    });
}