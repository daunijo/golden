// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Return', {
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
	supplier: function(frm){
		$.each(frm.doc.references, function(i, d) {
			d.party = frm.doc.supplier;
		})
		frm.refresh_fields("references");
	},
	from_warehouse: function(frm){
		$.each(frm.doc.items, function(i, d) {
			d.s_warehouse = frm.doc.from_warehouse;
		})
		frm.refresh_fields("items");
	},
	supplier_address: function(frm){
		if(frm.doc.supplier_address != undefined){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Address",
					name: frm.doc.supplier_address
				},
				callback: function (data) {
					if(data.message.address_line1 != undefined){
						line1 = data.message.address_line1
					}else{
						line1 = ""
					}
					if(data.message.address_line2 != undefined){
						line2 = "\n"+data.message.address_line2
					}else{
						line2 = ""
					}
					if(data.message.city != undefined){
						city = "\n"+data.message.city
					}else{
						city = ""
					}
					if(data.message.country != undefined){
						country = "\n"+data.message.country
					}else{
						country = ""
					}
					if(data.message.pincode != undefined){
						pincode = "\n"+data.message.pincode
					}else{
						pincode = ""
					}
					join = line1+line2+city+country+pincode;
					frm.set_value("address_display", join);
				}
			})
		}else{
			frm.set_value("address_display", "");
		}
	},
	debit_account: function(frm){
		$.each(frm.doc.references, function(i, d) {
			d.account = frm.doc.debit_account;
		})
		frm.refresh_fields("references");
	},
});
frappe.ui.form.on('Purchase Return Detail', {
	items_add: function(frm, cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
		if(!row.s_warehouse) row.s_warehouse = frm.doc.from_warehouse;
		frm.refresh_fields("items");
	},
	items_remove: function(frm, cdt, cdn) {
		calculate_total_quantity(frm, cdt, cdn);
	},
	item_code: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
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
	qty: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		d.amount = flt(d.qty) * flt(d.basic_rate);
		d.transfer_qty = flt(d.qty) * flt(d.conversion_factor);
		refresh_field('amount', d.name, 'items');
		refresh_field('transfer_qty', d.name, 'items');
		calculate_total_quantity(frm, cdt, cdn);
	},
	basic_rate: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		d.amount = flt(d.qty) * flt(d.basic_rate);
		refresh_field('amount', d.name, 'items');
		calculate_total_quantity(frm, cdt, cdn);
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

});
var calculate_total_quantity = function(frm) {
	var total_quantity = frappe.utils.sum(
		(frm.doc.items || []).map(function(i) {
			return (flt(i.qty) * flt(i.basic_rate));
		})
	);
	frm.set_value("total", total_quantity);
}
var calculate_total_return = function(frm) {
	var total_return = frappe.utils.sum(
		(frm.doc.references || []).map(function(i) {
			return (flt(i.debit_in_account_currency));
		})
	);
	frm.set_value("total_return", total_return);
}

cur_frm.set_query("supplier_address", function(frm) {
	return {
		query: "golden.golden.purchase.address_query",
		filters: {
			'link_name': cur_frm.doc.supplier
		}
	}
});
cur_frm.set_query("item_code", "items",  function (doc, cdt, cdn) {
	var c_doc= locals[cdt][cdn];
	return {
		query: "golden.golden.purchase.item_query",
		filters: {
			'supplier': cur_frm.doc.supplier
		}
	}
});
cur_frm.set_query("reference_name", "references",  function (doc, cdt, cdn) {
	var c_doc= locals[cdt][cdn];
	return {
		filters: {
			'supplier': cur_frm.doc.supplier,
			'docstatus': 1,
			'status': ["!=", "Paid"]
		}
	}
});
frappe.ui.form.on("Purchase Return Reference", {
	reference_name: function(frm, cdt, cdn) {
		row = locals[cdt][cdn];
		frappe.call({
			"method": "frappe.client.get",
			args: {
				doctype: "Purchase Invoice",
				name: row.reference_name
			},
			callback: function (data) {
				frappe.model.set_value(cdt, cdn, "net_total", data.message.net_total);
			}
		})
		calculate_total_return(frm, cdt, cdn);
	},
	debit_in_account_currency: function(frm, cdt, cdn) {
		calculate_total_return(frm, cdt, cdn);
	},
	references_add: function(frm, cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
		if(!row.party) row.party = frm.doc.supplier;
		if(!row.account) row.account = frm.doc.debit_account;
		frm.refresh_fields("references");
	},
	references_remove: function(frm, cdt, cdn) {
		calculate_total_return(frm, cdt, cdn);
	},
})
