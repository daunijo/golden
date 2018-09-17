// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Invoice Keeptrack', {
	setup: function(frm){
		frm.set_query('collector', function(doc) {
			return {
				query: "golden.golden.doctype.employee_settings.employee_settings.employee_query",
				filters: { 'department': 'collector' }
			}
		});
	},
	refresh: function(frm) {
		frm.events.set_read_only(frm);
		if(frm.doc.docstatus == 1 && frm.doc.status == "Submitted") {
			cur_frm.add_custom_button(__('Payment Entry'), cur_frm.cscript['Payment Entry'], __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
		}
		if(frm.doc.docstatus == 0 || frm.doc.__islocal){
			frm.add_custom_button(__('Sales Invoice'), function() {
				items = $.map(frm.doc.invoices, function(item,idx) {
					if(item.reference_doctype == 'Sales Invoice'){
						return item.invoice
					}
				})
				added_items = items.join(",")
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.invoice_keeptrack.invoice_keeptrack.get_sales_invoice2",
					source_doctype: "Sales Invoice",
					date_field: "posting_date",
					target: frm,
					setters: {
						customer: frm.doc.customer || undefined,
						grand_total: frm.doc.grand_total || undefined,
						invoice_keeptrack: frm.doc.invoice_keeptrack || undefined
					},
					get_query_filters: {
						docstatus: 1,
						name: ["not in", added_items]
					}
				})
			}, __("Get invoice from"));
			frm.add_custom_button(__('Sales Invoice Summary'), function() {
				items = $.map(frm.doc.invoices, function(item,idx) {
					if(item.reference_doctype == 'Sales Invoice Summary'){
						return item.invoice
					}
				})
				added_items = items.join(",")
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.invoice_keeptrack.invoice_keeptrack.get_si_summary",
					source_doctype: "Sales Invoice Summary",
					date_field: "posting_date",
					target: frm,
					setters: {
						customer: frm.doc.customer || undefined,
						total_invoice: frm.doc.total_invoice || undefined,
						invoice_keeptrack: frm.doc.invoice_keeptrack || undefined
					},
					get_query_filters: {
						docstatus: 1,
						name: ["not in", added_items]
					}
				})
			}, __("Get invoice from"));
			frm.add_custom_button(__('Sales Return'), function() {
				items = $.map(frm.doc.invoices, function(item,idx) {
					if(item.reference_doctype == 'Sales Return'){
						return item.invoice
					}
				})
				added_items = items.join(",")
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.invoice_keeptrack.invoice_keeptrack.get_sales_return",
					source_doctype: "Sales Return",
					date_field: "posting_date",
					target: frm,
					setters: {
						customer: frm.doc.customer || undefined,
						invoice_keeptrack: frm.doc.invoice_keeptrack || undefined
					},
					get_query_filters: {
						docstatus: 1,
						name: ["not in", added_items]
					}
				})
			}, __("Get invoice from"));
		}
	},
	validate: function(frm){
		frm.clear_table("customer_list");
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
						c.reference_doctype = d.reference_doctype;
						c.invoice = d.invoice;
						c.invoice_date = d.invoice_date;
						c.due_date = d.due_date;
						c.payment_date = d.payment_date;
						c.payment_amount = d.payment_amount;
						c.si_summary = d.si_summary;
						c.amount = d.amount;
					})
					frm.refresh_fields();
				}
			}
		})
	},
	collector: function(frm){
		if(frm.doc.collector){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Employee",
					filters:{
						name: frm.doc.collector,
					}
				},
				callback: function (data) {
					frm.set_value("collector_name", data.message.employee_name);
				}
			})
		}else{
			frm.set_value("collector_name", "");
		}
	}
});
cur_frm.cscript['Payment Entry'] = function() {
	frappe.model.open_mapped_doc({
		method: "golden.golden.stock.make_material_transfer",
		frm: cur_frm
	})
}
