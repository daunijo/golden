// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Budget', {
	refresh: function(frm) {
		frm.events.set_read_only(frm);
	},
	validate: function(frm){
		frm.refresh_fields();
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
	purchase_by_item_group: function(frm){
		frappe.set_route("query-report", "Purchase By Item Group", {"purchase_budget": frm.doc.name})
	},
	get_purchase_order: function(frm){
		frm.clear_table("details");
		return frappe.call({
			method: 'golden.golden.doctype.purchase_budget.purchase_budget.get_purchase_order',
			args: {
				start_date: frm.doc.start_date,
				end_date: frm.doc.end_date,
				budget1: frm.doc.budget_planning || 0,
				budget2: frm.doc.budget_revision || 0
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("details");
						c.po_date = d.po_date;
						c.purchase_order = d.purchase_order;
						c.po_amount = d.po_amount;
						c.purchase_receipt = d.purchase_receipt;
						c.pr_amount = d.pr_amount;
						c.percentage_budget_po = d.percentage_budget_po;
						c.percentage_budget_pr = d.percentage_budget_pr;
					})
					frm.events.calculate_total_po(frm);
					frm.events.calculate_total_pr(frm);
					frm.events.calculate_percentage_budget_po(frm);
					frm.events.calculate_percentage_budget_pr(frm);
					frm.refresh_fields();
				}
			}
		});
	},
	budget_planning: function(frm){
		frm.events.calculate_percentage_budget_po(frm);
		frm.events.calculate_percentage_budget_pr(frm);
	},
	budget_revision: function(frm){
		frm.events.calculate_percentage_budget_po(frm);
		frm.events.calculate_percentage_budget_pr(frm);
	},
	calculate_total_po: function(frm){
		var total_po = frappe.utils.sum(
			(frm.doc.details || []).map(function(i) {
				return (flt(i.po_amount));
			})
		);
		frm.set_value("total_purchase_order", total_po);
	},
	calculate_total_pr: function(frm){
		var total_pr = frappe.utils.sum(
			(frm.doc.details || []).map(function(i) {
				return (flt(i.pr_amount));
			})
		);
		frm.set_value("total_purchase_receipt", total_pr);
	},
	calculate_percentage_budget_po: function(frm){
		if(flt(frm.doc.budget_revision) == 0){
			var percen_po = flt(frm.doc.total_purchase_order) / flt(frm.doc.budget_planning) * 100
		}else{
			var percen_po = flt(frm.doc.total_purchase_order) / flt(frm.doc.budget_revision) * 100
		}
		frm.set_value("total_percentage_budget_po", percen_po);
	},
	calculate_percentage_budget_pr: function(frm){
		if(flt(frm.doc.budget_revision) == 0){
			var percen_pr = flt(frm.doc.total_purchase_receipt) / flt(frm.doc.budget_planning) * 100
		}else{
			var percen_pr = flt(frm.doc.total_purchase_receipt) / flt(frm.doc.budget_revision) * 100
		}
		frm.set_value("total_percentage_budget_pr", percen_pr);
	},
});
