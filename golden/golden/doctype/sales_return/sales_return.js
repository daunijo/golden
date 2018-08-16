// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Return', {
	refresh: function(frm) {
		frm.events.set_read_only(frm);
	},
	setup: function(frm){
		frm.set_query("to_warehouse", function (doc) {
			return {
				filters: [
					['type', '=', 'Location'],
				]
			}
		});
		frm.set_query('sales_person', function(doc) {
			return {
				query: "golden.golden.doctype.employee_settings.employee_settings.employee_query",
				filters: { 'department': 'sales' }
			}
		});
	},
	validate: function(frm){
		frm.clear_table("accounts");
		frm.events.set_expense_account(frm);
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
	customer: function(frm){
		if(frm.doc.customer){
			$.each(frm.doc.references, function(i, d) {
				d.party = frm.doc.customer;
			})
			// frm.refresh_fields("references");
			frm.events.set_debit_credit_account(frm);
			frm.events.set_references(frm);
		}
	},
	sales_person: function(frm){
		if(frm.doc.sales_person){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Employee",
					name: frm.doc.sales_person
				},
				callback: function (data) {
					frm.set_value("sales_name", data.message.employee_name);
				}
			})
		}else{
			frm.set_value("sales_name", "");
		}
	},
	set_debit_credit_account: function(frm){
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Company",
				name: frm.doc.company
			},
			callback: function (data) {
				frm.set_value("debit_account", data.message.default_sales_return_account);
				frm.set_value("credit_account", data.message.default_receivable_account);
				frm.set_value("to_warehouse", data.message.default_return_warehouse);
				frm.set_value("write_off_account", data.message.default_sales_return_write_off_account);
			}
		})
	},
	set_references: function(frm){
		frm.clear_table("references");
		return frappe.call({
			method: 'golden.golden.doctype.sales_return.sales_return.get_references',
			args: {
				customer: frm.doc.customer
			},
			callback: function(r, rt) {
				if(r.message) {
					$.each(r.message, function(i, d) {
						var c = frm.add_child("references");
						c.reference_name = d.reference_name;
						c.posting_date = d.posting_date;
						c.total_amount = d.total_amount;
						c.outstanding_amount = d.outstanding_amount;
						c.party = d.party;
						c.account = d.account;
					})
					// calculate_total_return(frm, cdt, cdn);
					// calculate_unallocated_amount(frm, cdt, cdn);
					frm.refresh_fields();
				}
			}
		});
	},
	customer_address: function(frm){
		if(frm.doc.customer_address != undefined){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Address",
					name: frm.doc.customer_address
				},
				callback: function (data) {
					if(data.message.address_line2 != undefined){
						line2 = "\n"+data.message.address_line2
					}else{
						line2 = ""
					}
					if(data.message.pincode != undefined){
						pincode = "\n"+data.message.pincode
					}else{
						pincode = ""
					}
					join = data.message.address_line1+line2+"\n"+data.message.city+"\n"+data.message.country+pincode;
					frm.set_value("address_display", join);
				}
			})
		}else{
			frm.set_value("address_display", "");
		}
	},
	to_warehouse: function(frm){
		$.each(frm.doc.items, function(i, d) {
			d.t_warehouse = frm.doc.to_warehouse;
		})
		frm.refresh_fields("items");
	},
	credit_account: function(frm){
		$.each(frm.doc.references, function(i, d) {
			d.account = frm.doc.credit_account;
		})
		frm.refresh_fields("references");
	},
	debit_account: function(frm){
		frm.events.set_expense_account(frm);
	},
	set_expense_account: function(frm){
		$.each(frm.doc.items, function(i, d) {
			d.expense_account = frm.doc.debit_account;
		})
		frm.refresh_fields("items");
	},
});
//Sales Return Detail (items)
frappe.ui.form.on('Sales Return Detail', {
	items_add: function(frm, cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
		if(!row.t_warehouse) row.t_warehouse = frm.doc.to_warehouse;
		frm.refresh_fields("items");
	},
	items_remove: function(frm, cdt, cdn) {
		calculate_total_quantity(frm, cdt, cdn);
		calculate_unallocated_amount(frm, cdt, cdn);
	},
	item_code: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "sales_invoice", "");
		frappe.model.set_value(cdt, cdn, "si_rate", "0");
		// calculate_total_quantity(frm, cdt, cdn);
		if(d.item_code) {
			var args = {
				'item_code'		: d.item_code,
				'warehouse'		: cstr(d.s_warehouse) || cstr(d.t_warehouse),
				'transfer_qty': d.transfer_qty,
				'serial_no'		: d.serial_no,
				'bom_no'			: d.bom_no,
				'expense_account'	: d.expense_account,
				'cost_center'	: d.cost_center,
				'company'			: frm.doc.company,
				'qty'				: d.qty
			};
			return frappe.call({
				doc: frm.doc,
				method: "get_item_details",
				args: args,
				callback: function(r) {
					if(r.message) {
						var d = locals[cdt][cdn];
						$.each(r.message, function(k, v) {
							d[k] = v;
						});
						refresh_field("items");
						erpnext.stock.select_batch_and_serial_no(frm, d);
					}
				}
			});
		}
	},
	sales_invoice: function(doc, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.sales_invoice && d.item_code){
			frappe.call({
				method: "golden.golden.doctype.sales_return.sales_return.get_item_rate",
				args:{
					parent: d.sales_invoice,
					item_code: d.item_code
				},
				callback: function (r) {
					if(r.message) {
						frappe.model.set_value(cdt, cdn, r.message);
					}
				}
			})
		}else{
			frappe.model.set_value(cdt, cdn, "si_rate", "0");
		}
	},
	qty: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		d.amount = flt(d.qty) * flt(d.basic_rate);
		d.transfer_qty = flt(d.qty) * flt(d.conversion_factor);
		refresh_field('amount', d.name, 'items');
		refresh_field('transfer_qty', d.name, 'items');
		calculate_total_quantity(frm, cdt, cdn);
		calculate_unallocated_amount(frm, cdt, cdn);
	},
	basic_rate: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		d.amount = flt(d.qty) * flt(d.basic_rate);
		refresh_field('amount', d.name, 'items');
		calculate_total_quantity(frm, cdt, cdn);
		// calculate_unallocated_amount(frm, cdt, cdn);
	},
	conversion_factor: function(frm, cdt, cdn){
		d.transfer_qty = flt(d.qty) * flt(d.conversion_factor);
		refresh_field('transfer_qty', d.name, 'items');
	},
	uom: function(doc, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.uom && d.item_code){
			return frappe.call({
				method: "erpnext.stock.doctype.stock_entry.stock_entry.get_uom_details",
				args: {
					item_code: d.item_code,
					uom: d.uom,
					qty: d.qty
				},
				callback: function(r) {
					if(r.message) {
						frappe.model.set_value(cdt, cdn, r.message);
					}
				}
			});
		}
	},
})
var calculate_total_quantity = function(frm) {
	var total_quantity = frappe.utils.sum(
		(frm.doc.items || []).map(function(i) {
			return (flt(i.qty) * flt(i.basic_rate) * flt(i.conversion_factor));
		})
	);
	frm.set_value("total", total_quantity);
	var total_2 = frappe.utils.sum(
		(frm.doc.items || []).map(function(i) {
			return (flt(i.qty) * flt(i.si_rate) * flt(i.conversion_factor));
		})
	);
	frm.set_value("total_2", total_2);
}

cur_frm.set_query("customer_address", function(frm) {
	return {
		query: "golden.golden.purchase.address_query",
		filters: {
			'link_name': cur_frm.doc.customer
		}
	}
});
cur_frm.set_query("debit_account", function(frm) {
	return {
		query: "erpnext.controllers.queries.get_expense_account",
	}
});
cur_frm.set_query("item_code", "items", function (doc, cdt, cdn) {
	var c_doc= locals[cdt][cdn];
	return {
		query: "golden.golden.selling.item_query",
		filters: {
			'customer': cur_frm.doc.customer,
			'sales': cur_frm.doc.sales_person
		}
	}
});
cur_frm.set_query("sales_invoice", "items",  function (doc, cdt, cdn) {
	var c_doc= locals[cdt][cdn];
	return {
		query: "golden.golden.selling.si_query",
		filters: {
			'customer': cur_frm.doc.customer,
			'item_code': c_doc.item_code,
			'sales': cur_frm.doc.sales_person
		}
	}
});
cur_frm.set_query("reference_name", "references", function (doc, cdt, cdn) {
	items = $.map( cur_frm.doc.references, function(item,idx) { return item.reference_name } )
	added_items = items.join(",")
	var c_doc= locals[cdt][cdn];
	return {
		filters: {
			'customer': cur_frm.doc.customer,
			'docstatus': 1,
			'status': ['!=', 'Paid'],
			'name': ["not in", added_items]
		}
	}
});
frappe.ui.form.on("Sales Return Reference", {
	reference_name: function(frm, cdt, cdn) {
		row = locals[cdt][cdn];
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Sales Invoice",
				name: row.reference_name
			},
			callback: function (data) {
				frappe.model.set_value(cdt, cdn, "total_amount", data.message.grand_total);
				frappe.model.set_value(cdt, cdn, "outstanding_amount", data.message.outstanding_amount);
			}
		})
		calculate_total_return(frm, cdt, cdn);
		// calculate_unallocated_amount(frm, cdt, cdn);
	},
	credit_in_account_currency: function(frm, cdt, cdn) {
		calculate_total_return(frm, cdt, cdn);
		calculate_unallocated_amount(frm, cdt, cdn);
	},
	references_add: function(frm, cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
		if(!row.party) row.party = frm.doc.customer;
		if(!row.account) row.account = frm.doc.debit_account;
		frm.refresh_fields("references");
	},
	references_remove: function(frm, cdt, cdn) {
		calculate_total_return(frm, cdt, cdn);
		calculate_unallocated_amount(frm, cdt, cdn);
	},
})
var calculate_total_return = function(frm) {
	var total_return = frappe.utils.sum(
		(frm.doc.references || []).map(function(i) {
			return (flt(i.credit_in_account_currency));
		})
	);
	frm.set_value("total_return", total_return);
}
var calculate_unallocated_amount = function(frm) {
	var return_amount = frappe.utils.sum(
		(frm.doc.references || []).map(function(i) {
			return (flt(i.credit_in_account_currency));
		})
	);
	var total_2 = frappe.utils.sum(
		(frm.doc.items || []).map(function(i) {
			return (flt(i.qty) * flt(i.si_rate) * flt(i.conversion_factor));
		})
	);
	var unallocated = flt(total_2) - flt(return_amount);
	frm.set_value("unallocated_amount", unallocated);
}
