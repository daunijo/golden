// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Summary Generator', {
	setup: function(frm) {

	},
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
	generate: function(frm){
		frm.events.generate_customers(frm);
		frm.events.generate_details(frm);
	},
	generate_customers: function(frm){
		return frappe.call({
			method: 'golden.golden.doctype.summary_generator.summary_generator.get_customers',
			args: {
				start: frm.doc.start_date,
				end: frm.doc.end_date,
				territory: frm.doc.territory || ""
			},
			callback: function(r, rt) {
				if(r.message) {
					frm.clear_table("customers");
					$.each(r.message, function(i, d) {
						var c = frm.add_child("customers");
						c.customer = d.customer;
						c.customer_name = d.customer_name;
						// c.sales = d.sales;
					})
					frm.refresh_fields();
				}
			}
		})
	},
	generate_details: function(frm){
		return frappe.call({
			method: 'golden.golden.doctype.summary_generator.summary_generator.get_details',
			args: {
				start: frm.doc.start_date,
				end: frm.doc.end_date,
				territory: frm.doc.territory || ""
			},
			callback: function(r, rt) {
				if(r.message) {
					frm.clear_table("details");
					$.each(r.message, function(i, d) {
						var c = frm.add_child("details");
						c.customer = d.customer;
						c.customer_name = d.customer_name;
						c.reference_doctype = d.reference_doctype;
						c.reference_name = d.reference_name;
						c.invoice_date = d.posting_date;
						c.amount = d.amount;
						c.due_date = d.due_date;
						c.sales_name = d.sales_name;
					})
					frm.refresh_fields();
				}
			}
		})
	},
});
