// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Invoice Keeptrack', {
	refresh: function(frm) {
		frm.events.set_read_only(frm);
		if(frm.doc.docstatus == 1 && frm.doc.status == "Submitted") {
			cur_frm.add_custom_button(__('Payment Entry'), cur_frm.cscript['Payment Entry'], __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
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
	get_sales_invoice: function(frm){
		return frappe.call({
			method: 'golden.golden.doctype.invoice_keeptrack.invoice_keeptrack.get_sales_invoice',
			args: {
				docstatus: 1
			},
			callback: function(r, rt) {
				if(r.message) {
					frm.clear_table("invoices");
					$.each(r.message, function(i, d) {
						var c = frm.add_child("invoices");
						c.customer = d.customer;
						c.customer_name = d.customer_name;
						c.si_summary = d.si_summary;
						c.amount = d.amount;
					})
					frm.refresh_fields();
				}
			}
		})
	},
});
cur_frm.cscript['Payment Entry'] = function() {
	frappe.model.open_mapped_doc({
		method: "golden.golden.stock.make_material_transfer",
		frm: cur_frm
	})
}
