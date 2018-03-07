// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Target', {
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
		frm.clear_table("details");
		return frappe.call({
			method: 'golden.golden.doctype.sales_target.sales_target.get_sales_invoice',
			args: {
				start_date: frm.doc.start_date,
				end_date: frm.doc.end_date
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("details");
						c.customer = d.customer;
						c.customer_name = d.customer_name;
						c.sales_invoice_date = d.sales_invoice_date;
						c.sales_invoice = d.sales_invoice;
						c.invoice_amount = d.grand_total;
						c.payment_date = d.payment_date;
						c.payment_amount = d.payment_amount;
						c.difference_day = d.difference_day;
					})
					frm.refresh_fields();
				}
			}
		})
	},
});
