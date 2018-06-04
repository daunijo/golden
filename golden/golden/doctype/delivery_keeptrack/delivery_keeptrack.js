// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Keeptrack', {
	refresh: function(frm) {
		frm.events.set_read_only(frm);
		calculate_total_box(frm);
		if(frm.doc.docstatus == 0 || frm.doc.__islocal){
			frm.add_custom_button(__("Delivery Order"), function() {
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.delivery_keeptrack.delivery_keeptrack.get_delivery_order",
					source_doctype: "Delivery Order Detail",
					target: frm,
					setters:  {
					},
					get_query_filters: {
						docstatus: 1,
						delivery_keeptrack: ""
					}
				})
			}, __("Get details from"));
			frm.add_custom_button(__("Delivery Return"), function() {
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.delivery_keeptrack.delivery_keeptrack.get_delivery_order",
					source_doctype: "Delivery Order Detail",
					target: frm,
					setters:  {
					},
					get_query_filters: {
						docstatus: 1,
						delivery_return: ["!=", ""]
					}
				})
			}, __("Get details from"));
			frm.add_custom_button(__("Packing List"), function() {
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.delivery_keeptrack.delivery_keeptrack.get_packing",
					source_doctype: "Packing",
					target: frm,
					setters:  {
					},
					get_query_filters: {
						docstatus: 1
					}
				})
			}, __("Get details from"));
		}
		if(frm.doc.docstatus == 1) {
			if(frm.doc.is_completed == 0 && frm.doc.delivery_return == undefined){
				cur_frm.add_custom_button(__('Delivery Return'), cur_frm.cscript['Delivery Return'], __("Make"));
				cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
			}
			if(frm.doc.is_completed == 0){
				cur_frm.add_custom_button(__('Set as Complete'), cur_frm.cscript['Set as Complete']);
			}
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
cur_frm.cscript['Delivery Return'] = function() {
	frappe.model.open_mapped_doc({
		method: "golden.golden.doctype.delivery_keeptrack.delivery_keeptrack.make_delivery_return",
		frm: cur_frm
	})
}
cur_frm.cscript['Set as Complete'] = function() {
	frappe.call({
		method: "golden.golden.doctype.delivery_keeptrack.delivery_keeptrack.set_complete",
		args: {
			name: cur_frm.doc.name
		},
		callback: function(r){
			cur_frm.reload_doc();
		},
	});
}
frappe.ui.form.on('Delivery Keeptrack Detail', {
	details_add: function(frm, cdt, cdn) {
		calculate_total_box(frm, cdt, cdn);
	},
	details_remove: function(frm, cdt, cdn) {
		calculate_total_box(frm, cdt, cdn);
	},
})
var calculate_total_box = function(frm) {
	var total_box = frappe.utils.sum(
		(frm.doc.details || []).map(function(i) {
			return (flt(i.box));
		})
	);
	frm.set_value("total_box", total_box);
}
