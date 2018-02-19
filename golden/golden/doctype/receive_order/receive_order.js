// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Receive Order', {
	setup: function(frm){
		frm.set_query('accepted_location', function(doc) {
			return {
				filters: { 'is_group': 0 }
			}
		});
	},
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 || frm.doc.__islocal) {
			frm.add_custom_button(__("Get Purchase Order"), function() {
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.receive_order.receive_order.get_purchase_order",
					source_doctype: "Purchase Order",
					target: frm,
					setters:  {
						company: frm.doc.company || undefined,
					},
					get_query_filters: {
						docstatus: 1,
						company: frm.doc.company,
						status: ["in", "To Receive and Bill, To Receive"]
					}
				})
			});
		}
		if(frm.doc.docstatus == 0 || frm.doc.__islocal){
			frm.events.set_read_only(frm);
		}
	},
	set_posting_time: function(frm){
		frm.events.set_read_only(frm);
	},
	set_read_only: function(frm){
		if(frm.doc.set_posting_time == 1){
			frm.set_df_property("posting_date", "read_only", false);
			frm.set_df_property("posting_time", "read_only", false);
		}else{
			frm.set_df_property("posting_date", "read_only", true);
			frm.set_df_property("posting_time", "read_only", true);
		}
	},
});
