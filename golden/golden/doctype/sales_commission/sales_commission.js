// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Commission', {
	setup: function(frm){
		frm.set_query("sales", function (doc) {
			return {
				query: "golden.golden.doctype.employee_settings.employee_settings.employee_query",
				filters: { 'department': 'sales' }
			}
		});
		frm.set_query("sales_target", function (doc) {
			return {
				filters: [
					['sales', '=', frm.doc.sales],
					['docstatus', '=', 1],
					['sales_commission', '=', '']
				]
			}
		});
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
	sales: function(frm){
		if(frm.doc.sales){
			frm.set_value("sales_target", "");
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Employee",
					filters:{
						name: frm.doc.sales,
					}
				},
				callback: function (data) {
					if(data.message){
						frm.set_value("sales_name", data.message.employee_name);
					}
				}
			})
		}else{
			frm.set_value("sales_name", "");
		}
	},
	sales_target: function(frm){
		if(frm.doc.sales_target){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Sales Target",
					filters:{
						name: frm.doc.sales_target,
					}
				},
				callback: function (data) {
					if(data.message){
						frm.set_value("start_date", data.message.start_date);
						frm.set_value("end_date", data.message.end_date);
						frm.set_value("omset", data.message.total_sales_invoice);
						if(data.message.target_revision){
							frm.set_value("target", data.message.target_revision);
						}else{
							frm.set_value("target", data.message.target_planning);
						}
					}
				}
			})
		}else{
			frm.set_value("start_date", "");
			frm.set_value("end_date", "");
			frm.set_value("omset", "");
		}
	},
	generate: function(frm){
		frm.events.get_invoices(frm);
		frm.events.get_returns(frm);
		frm.events.get_payments(frm);
	},
	get_invoices: function(frm){
		frm.clear_table("invoices");
		return frappe.call({
			method: 'golden.golden.doctype.sales_commission.sales_commission.get_invoices',
			args: {
				sales: frm.doc.sales,
				sales_target: frm.doc.sales_target,
				start_date: frm.doc.start_date,
				end_date: frm.doc.end_date
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("invoices");
						c.si_date = d.sales_invoice_date;
						c.sales_invoice = d.sales_invoice;
						c.amount = d.amount;
					})
					frm.events.calculate_total_invoice(frm);
					frm.events.calculate_percentage_invoice(frm);
					frm.events.calculate_invoice_commission(frm);
					// frm.events.calculate_total_commission(frm);
					frm.refresh_fields();
				}
			}
		});
	},
	get_returns: function(frm){
		frm.clear_table("returns");
		return frappe.call({
			method: 'golden.golden.doctype.sales_commission.sales_commission.get_returns',
			args: {
				sales: frm.doc.sales,
				sales_target: frm.doc.sales_target,
				start_date: frm.doc.start_date,
				end_date: frm.doc.end_date
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("returns");
						c.return_date = d.return_date;
						c.sales_return = d.sales_return;
						c.amount = d.amount;
					})
					frm.events.calculate_total_return(frm);
					frm.events.calculate_percentage_invoice(frm);
					frm.events.calculate_percentage_return(frm);
					frm.events.calculate_return_commission(frm);
					// frm.events.calculate_total_commission(frm);
					frm.refresh_fields();
				}
			}
		});
	},
	get_payments: function(frm){
		frm.clear_table("payments");
		return frappe.call({
			method: 'golden.golden.doctype.sales_commission.sales_commission.get_payments',
			args: {
				sales: frm.doc.sales,
				sales_target: frm.doc.sales_target,
				start_date: frm.doc.start_date,
				end_date: frm.doc.end_date
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("payments");
						c.payment_entry = d.payment_entry;
						c.payment_date = d.payment_date;
						c.sales_invoice = d.sales_invoice;
						c.payment_amount = d.payment_amount;
						c.invoice_date = d.invoice_date;
						c.date_diff = d.date_diff;
						c.payment_commission = d.payment_commission;
					})
					frm.events.calculate_total_return(frm);
					frm.events.calculate_percentage_invoice(frm);
					frm.events.calculate_percentage_return(frm);
					frm.events.calculate_invoice_commission(frm);
					frm.events.calculate_return_commission(frm);
					frm.events.calculate_total_payment_commission(frm);
					// frm.events.calculate_total_commission(frm);
					frm.refresh_fields();
				}
			}
		});
	},
	calculate_total_invoice: function(frm){
		var total_invoice = frappe.utils.sum(
			(frm.doc.invoices || []).map(function(i) {
				return (flt(i.amount));
			})
		);
		frm.set_value("total_invoice", total_invoice);
	},
	calculate_total_return: function(frm){
		var total_returns = frappe.utils.sum(
			(frm.doc.returns || []).map(function(i) {
				return (flt(i.amount));
			})
		);
		frm.set_value("total_return", total_returns);
	},
	calculate_percentage_invoice: function(frm){
		var percent_inv = ((flt(frm.doc.total_invoice) - flt(frm.doc.total_return))/ flt(frm.doc.target)) * 100;
		frm.set_value("percentage_invoice", percent_inv)
	},
	calculate_percentage_return: function(frm){
		var percent_ret = (flt(frm.doc.total_return) / flt(frm.doc.total_invoice)) * 100;
		frm.set_value("percentage_return", percent_ret);
		frm.refresh_fields();
	},
	calculate_invoice_commission: function(frm){
		frappe.call({
			method: "golden.golden.doctype.sales_commission.sales_commission.calculate_invoice",
			args:{
				sales: frm.doc.sales,
				percentage: frm.doc.percentage_invoice,
				total_invoice: frm.doc.total_invoice
			},
			callback: function (r) {
				if(r.message) {
					frm.set_value( r.message);
				}
			}
		})
	},
	calculate_return_commission: function(frm){
		frappe.call({
			method: "golden.golden.doctype.sales_commission.sales_commission.calculate_return",
			args:{
				sales: frm.doc.sales,
				percentage: frm.doc.percentage_return || 0,
				total_return: frm.doc.total_return
			},
			callback: function (r) {
				if(r.message) {
					frm.set_value( r.message);
				}
			}
		})
	},
	calculate_total_payment_commission: function(frm){
		var total_payment_commission = frappe.utils.sum(
			(frm.doc.payments || []).map(function(i) {
				return (flt(i.payment_commission));
			})
		);
		frm.set_value("payment_commission", total_payment_commission);
	},
	invoice_commission: function(frm){
		frm.events.calculate_total_commission(frm);
	},
	return_commission: function(frm){
		frm.events.calculate_total_commission(frm);
	},
	payment_commission: function(frm){
		frm.events.calculate_total_commission(frm);
	},
	calculate_total_commission: function(frm){
		var percentage = flt(frm.doc.percentage_invoice_result) + flt(frm.doc.percentage_return_result);
		var amount = flt(frm.doc.total_invoice) - flt(frm.doc.total_return);
		var commission = flt(amount) * (flt(percentage) / 100);
		var total_commission = flt(commission) + flt(frm.doc.payment_commission);
		// var total_commission = flt(frm.doc.invoice_commission) + flt(frm.doc.return_commission) + flt(frm.doc.payment_commission);
		frm.set_value("total_commission", total_commission);
	},
});
