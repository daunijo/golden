// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Return', {
	onload: function(frm){
		frm.set_query("driver", function(doc) {
			return {
				query: "golden.golden.doctype.employee_settings.employee_settings.employee_query",
				filters: { 'department': 'driver' }
			}
		});
		frm.set_query("helper", function(doc) {
			return {
				query: "golden.golden.doctype.employee_settings.employee_settings.employee_query",
				filters: { 'department': 'helper' }
			}
		});
	},
	refresh: function(frm) {
		frm.events.set_read_only(frm);
		calculate_total_box(frm);
		if(frm.doc.docstatus == 0 || frm.doc.__islocal){
			frm.add_custom_button(__("Delivery Keeptrack"), function() {
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.delivery_keeptrack.delivery_keeptrack.make_delivery_return",
					source_doctype: "Delivery Keeptrack",
					target: frm,
					setters:  {
					},
					get_query_filters: {
						docstatus: 1,
						is_completed: 0
					}
				})
			}, __("Get details from"));
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
frappe.ui.form.on('Delivery Return Detail', {
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
