// Copyright (c) 2019, Dexciss and contributors
// For license information, please see license.txt

frappe.ui.form.on('Campaigns Designer', {
    refresh: function(frm) {
        frappe.call({
            method: 'get_cal',
            doc: frm.doc,
            callback:function(r){
                if(r.message)
                {
                if (frm.doc.docstatus==1)
                { 
                    frm.add_custom_button(__('Re-Create Campaign'),function(){
                    frappe.call({
                    method:"on_submit",
                    doc: frm.doc,
                    callback:function(r){
                        if(r.message)
                        {
                        frappe.msgprint("Campaign is created")
                        frm.refresh()
                        }
                    }})
                    })
                }
            }
        }
    })
       
        frm.set_df_property('agents_list', 'cannot_add_rows', 1);
		frm.set_df_property("filters_section", "hidden", 1);
		frm.trigger('set_options');
		frm.trigger('render_filters_table');

        if(frm.doc.docstatus == 1){
            frappe.model.get_value("Campaigns",{"campaigns_name":frm.doc.name}, "status", function(value) {
                console.log(value)
            if(value.status=="Running"){
            frm.add_custom_button(__('Update Contact'), function() {
               const filters = frm.filters.reduce((acc, filter) => {
                return Object.assign(acc, {
                    [filter[1]]: [filter[2], filter[3]]
                });
            }, {});
            frappe.call({
                method: 'b2b_marketing.b2b_marketing.doctype.campaigns_designer.campaigns_designer.update_contact_list',
                freeze: true,
                freeze_message: __('Creating Contact'),
                args: {
                    filters:filters,
                    self:frm.doc.name
                },
                callback: function(r) {
                    frm.refresh_field("total_available_contacts")
                    var arr = r.message;

                    frappe.msgprint(__("Contacts updated as per the filter.{0} new contacts have been added in the campaign.",[r.message]))
                }
            });
            }).addClass('btn-primary');
        }
        })
        }
	},
    before_submit: function(frm) {
        // Ensure filters exist
        const filters = (frm.filters || []).reduce((acc, filter) => {
            console.log(acc)
            acc[filter[1]] = [filter[2], filter[3]];
            return acc;
        }, {});

        const filters_json = JSON.stringify(filters);
        frm.set_value('filters', filters_json);
        // Make the server call
        frappe.call({
            method: 'b2b_marketing.b2b_marketing.doctype.campaigns_designer.campaigns_designer.get_contact_list',
            args: {
                filters: filters,
                name: frm.doc.name,
                doc:null
            },
            callback: function(r) {
                const arr = r.message;
                // console.log("Response data:", arr);
                const contact_filters= JSON.stringify(arr);
                console.log("datajdjdbj",contact_filters)
                frm.set_value('contact_filters', contact_filters);
    
                // Check for errors in the response
                if (arr.error) {
                    frappe.msgprint(arr.error);
                    frappe.validated = false;
                    return;
                }
    
                // Clear and populate the contact list table
                frm.clear_table('contact_list');
                arr.forEach(contact => {
                    if (contact.contact) {
                        let child = frm.add_child('contact_list');
                        child.contact = contact.contact;
                        child.organization = contact.organization;
                        child.phone = contact.phone;
                        child.mobile = contact.mobile;
                        child.email = contact.email;
                        child.corporate_phone = contact.corporate_phone;
                        child.organization_contact = contact.organization_contact;
                    } else {
                        frm.set_value('total_available_contacts', contact.total_available_contacts);
                    }
                });

                // Refresh the fields
                frm.refresh_field("contact_list");
                frm.refresh_field('total_available_contacts');
                frm.refresh_field("max_number_of_contacts")
            }
        });
    },
	set_options: function(frm) {
		let aggregate_based_on_fields = [];
		const doctype = 'Campaign Contact';

		if (doctype) {
			frappe.model.with_doctype(doctype, () => {
				frappe.get_meta(doctype).fields.map(df => {
					if (frappe.model.numeric_fieldtypes.includes(df.fieldtype)) {
						if (df.fieldtype == 'Currency') {
							if (!df.options || df.options !== 'Company:company:default_currency') {
								return;
							}
						}
						aggregate_based_on_fields.push({label: df.label, value: df.fieldname});
					}
				});

				frm.set_df_property('aggregate_function_based_on', 'options', aggregate_based_on_fields);
			});
		}
	},
	render_filters_table: function(frm) {
		frm.set_df_property("filters_section", "hidden", 0);

		let wrapper = $(frm.get_field('filter_contact').wrapper).empty();
		frm.filter_table = $(`<table class="table table-bordered" style="cursor:pointer; margin:0px;">
			<thead>
				<tr>
					<th style="width: 33%">${__('Filter')}</th>
					<th style="width: 33%">${__('Condition')}</th>
					<th>${__('Value')}</th>
				</tr>
			</thead>
			<tbody></tbody>
		</table>`).appendTo(wrapper);
		$(`<p class="text-muted small">${__("Click table to edit")}</p>`).appendTo(wrapper);


		frm.filters = JSON.parse(frm.doc.filter_contact || '[]');

		frm.trigger('set_filters_in_table');

		frm.filter_table.on('click', () => {
			let dialog = new frappe.ui.Dialog({
				title: __('Set Filters'),
				fields: [{
					fieldtype: 'HTML',
					fieldname: 'filter_area',
				}],
				primary_action: function() {
					let values = this.get_values();
					if (values) {
						this.hide();
						frm.filters = frm.filter_group.get_filters();
						frm.set_value('filter_contact', JSON.stringify(frm.filters));
						frm.trigger('set_filters_in_table');
					}
				},
				primary_action_label: "Set"
			});

			frappe.dashboards.filters_dialog = dialog;

			frm.filter_group = new frappe.ui.FilterGroup({
				parent: dialog.get_field('filter_area').$wrapper,
				doctype: 'Campaign Contact',
				on_change: () => {},
			});

			frm.filter_group.add_filters_to_filter_group(frm.filters);

			dialog.show();
			dialog.set_values(frm.filters);
		});

	},

	set_filters_in_table: function(frm) {
		if (!frm.filters.length) {
			const filter_row = $(`<tr><td colspan="3" class="text-muted text-center">
				${__("Click to Set Filters")}</td></tr>`);
			frm.filter_table.find('tbody').html(filter_row);
		} else {
			let filter_rows = '';
			frm.filters.forEach(filter => {
				filter_rows +=
					`<tr>
						<td>${filter[1]}</td>
						<td>${filter[2] || ""}</td>
						<td>${filter[3]}</td>
					</tr>`;

			});
			frm.filter_table.find('tbody').html(filter_rows);
		}
	},

	start_on: function(frm) {
        return frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.campaigns_designer.campaigns_designer.get_days",
        args: {
                start_date: frm.doc.start_on,
                end_date :frm.doc.end_on,
                company:frm.doc.company
            },
            callback: function(r)
            {
                frm.set_value("days", r.message);
            }
            });
        },
	end_on: function(frm) {
        if (frm.doc.end_on && frm.doc.start_on) 
        {
            if (frm.doc.start_on > frm.doc.end_on) 
            {
                frappe.msgprint(__("You cannot select 'End On' before 'Start On'"));
                frm.doc.end_on = "";
                refresh_field('end_on');
            }
        }
        return frm.call({
        method:"b2b_marketing.b2b_marketing.doctype.campaigns_designer.campaigns_designer.get_days",
        args: {
                start_date: frm.doc.start_on,
                end_date :frm.doc.end_on,
                company:frm.doc.company
            },
            callback: function(r)
            {
                frm.set_value("days", r.message);
            }
            });
        },
    onload: function(frm){
        frm.set_query('agent_name', function(doc) {
            return {
                filters: {
                    "is_group":1,
                }
            };
        });
        frm.set_query('cost_center', function(doc) {
            return {
                filters: {
                    "is_group":0
                }
            };
        });
        frm.set_query('script_template', function(doc) {
            return {
                filters: {
                    "is_call_script":1
                }
            };
        });
        frm.trigger('set_invoicing_frequency_property');
        frm.trigger('set_linkedin_operator');
    },
    set_invoicing_frequency_property: function(frm) {
        if(frm.doc.invoice_policy =="Fixed Charge")
        {
            frm.set_df_property("invoicing_frequency", "reqd", 1);
        }
        else
        {
            frm.set_df_property("invoicing_frequency", "reqd", 0);
        }
    },
    agent_name: function(frm){
            return frm.call('set_sub_agents').then(() => {
            frm.refresh_field('agents_list');
        });
    },
    fetch_agents: function(frm){
        return frm.call('set_sub_agents').then(() => {
    });
    },
	invoice_policy: function (frm) {
		frm.trigger('set_invoicing_frequency_property');
	},
	set_linkedin_operator: function(frm){
	    if (frm.doc.linkedin_count_number > 0)
	    {
	        frm.set_df_property("linkedin_count_operator", "reqd", 1);
	    }
	    else
	    {
	        frm.set_df_property("linkedin_count_operator", "reqd", 0);
	    }
	},
	linkedin_count_number :function(frm){
	    frm.trigger('set_linkedin_operator');
	},

});

