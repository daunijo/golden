// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Order', {
	setup: function(frm){
		frm.set_query("packing", "details", function (doc, cdt, cdn) {
			var c_doc= locals[cdt][cdn];
			return {
				filters: {
					'docstatus': 1
				}
			}
		});
	},
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 || frm.doc.__islocal){
			frm.events.set_read_only(frm);
			frm.events.get_packing_list(frm);
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
	get_packing_list: function(frm){
		if(frm.doc.docstatus == 0 || frm.doc.__islocal) {
			frm.add_custom_button(__("Get Packing List"), function() {
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.delivery_order.delivery_order.get_packing_list",
					source_doctype: "Packing",
					target: frm,
					setters:  {
						company: frm.doc.company || undefined,
					},
					get_query_filters: {
						docstatus: 1,
					}
				})
			});
		}
	},
});
frappe.ui.form.on("Delivery Order Detail", {
	packing: function(doc, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.packing){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Packing",
					filters:{
						name: d.packing,
					}
				},
				callback: function (data) {
					frappe.model.set_value(cdt, cdn, "customer", data.message.customer);
					frappe.model.set_value(cdt, cdn, "customer_name", data.message.customer_name);
					frappe.model.set_value(cdt, cdn, "packing_date", data.message.posting_date);
					frappe.model.set_value(cdt, cdn, "total_box", data.message.total_box);
				}
			})
		}
	}
})
