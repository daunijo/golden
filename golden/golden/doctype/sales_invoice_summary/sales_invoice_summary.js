// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice Summary', {
	refresh: function(frm) {
		frm.events.set_read_only(frm);
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
			method: 'golden.golden.doctype.sales_invoice_summary.sales_invoice_summary.get_sales_invoice',
			args: {
				start: frm.doc.start_date,
				end: frm.doc.end_date,
				sales_person: frm.doc.sales || undefined
			},
			callback: function(r, rt) {
				if(r.message) {
					frm.clear_table("invoices");
					$.each(r.message, function(i, d) {
						var c = frm.add_child("invoices");
						c.customer = d.customer;
						c.customer_name = d.customer_name;
						c.sales_invoice = d.si_name;
						c.invoice_date = d.posting_date;
						c.amount = d.amount;
						c.due_date = d.due_date;
					})
					frm.refresh_fields();
					frm.events.set_total_invoice(frm);
				}
			}
		})
	},
	set_total_invoice: function(frm) {
		var total_inv = 0.0;
		$.each(frm.doc.invoices, function(i, row) {
			total_inv += flt(row.amount);
		})
		frm.set_value("total_invoice", Math.abs(total_inv));
	},
});
frappe.ui.form.on('Sales Invoice Summary Detail', {
	invoices_add: function(frm, cdt, cdn) {
		calculate_total_invoice(frm, cdt, cdn);
	},
	invoices_remove: function(frm, cdt, cdn) {
		calculate_total_invoice(frm, cdt, cdn);
	},
})
var calculate_total_invoice = function(frm) {
	var total_invoice = frappe.utils.sum(
		(frm.doc.invoices || []).map(function(i) {
			return (flt(i.amount));
		})
	);
	frm.set_value("total_invoice", total_invoice);
}
