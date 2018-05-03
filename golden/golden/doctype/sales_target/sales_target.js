// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Target', {
	setup: function(frm){
		frm.set_query("sales", function (doc) {
			return {
				filters: [
					['department', '=', 'Sales']
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
	get_sales_invoice: function(frm){
		frm.clear_table("details");
		return frappe.call({
			method: 'golden.golden.doctype.sales_target.sales_target.get_sales_invoice',
			args: {
				sales: frm.doc.sales,
				start_date: frm.doc.start_date,
				end_date: frm.doc.end_date,
				target1: frm.doc.target_planning || 0,
				target2: frm.doc.target_revision || 0
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
						c.contribution = d.contribution;
					})
					frm.events.calculate_total_invoice(frm);
					frm.events.calculate_total_payment(frm);
					frm.events.calculate_average_day(frm);
					frm.events.calculate_percentage_si(frm);
					frm.events.calculate_percentage_payment(frm);
					frm.refresh_fields();
				}
			}
		});
	},
	target_planning: function(frm){
		frm.events.calculate_percentage_si(frm);
		frm.events.calculate_percentage_payment(frm);
	},
	target_revision: function(frm){
		frm.events.calculate_percentage_si(frm);
		frm.events.calculate_percentage_payment(frm);
	},
	collect_planning: function(frm){
		frm.events.calculate_percentage_si(frm);
		frm.events.calculate_percentage_payment(frm);
	},
	collect_revision: function(frm){
		frm.events.calculate_percentage_si(frm);
		frm.events.calculate_percentage_payment(frm);
	},
	calculate_total_invoice: function(frm){
		var total_invoice = frappe.utils.sum(
			(frm.doc.details || []).map(function(i) {
				return (flt(i.invoice_amount));
			})
		);
		frm.set_value("total_sales_invoice", total_invoice);
	},
	calculate_total_payment: function(frm){
		var total_payment = frappe.utils.sum(
			(frm.doc.details || []).map(function(i) {
				return (flt(i.payment_amount));
			})
		);
		frm.set_value("total_payment", total_payment);
	},
	calculate_average_day: function(frm){
		var total_days = frappe.utils.sum(
			(frm.doc.details || []).map(function(i) {
				return (flt(i.difference_day) * flt(i.contribution) / 100);
			})
		);
		// var count = frappe.utils.sum(
		// 	(frm.doc.details || []).map(function(i) {
		// 		return (1);
		// 	})
		// );
		// var avg_days = flt(total_days) / flt(count)
		frm.set_value("avg_day_collected", total_days);
	},
	calculate_percentage_si: function(frm){
		if(flt(frm.doc.target_revision) == 0){
			var percen_si = flt(frm.doc.total_sales_invoice) / flt(frm.doc.target_planning) * 100
		}else{
			var percen_si = flt(frm.doc.total_sales_invoice) / flt(frm.doc.target_revision) * 100
		}
		frm.set_value("total_percentage_target_si", percen_si);
	},
	calculate_percentage_payment: function(frm){
		if(flt(frm.doc.collect_planning) > 1){
			if(flt(frm.doc.collect_revision) == 0){
				var percen_si = flt(frm.doc.total_payment) / flt(frm.doc.collect_planning) * 100
			}else{
				var percen_si = flt(frm.doc.total_payment) / flt(frm.doc.collect_revision) * 100
			}
			frm.set_value("total_percentage_target_payment", percen_si);
		}else{
			frm.set_value("total_percentage_target_payment", 0);
		}
	},
});
