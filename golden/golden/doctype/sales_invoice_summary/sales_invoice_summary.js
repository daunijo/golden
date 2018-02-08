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
				docstatus: 1
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
				}
			}
		})
	},
});
