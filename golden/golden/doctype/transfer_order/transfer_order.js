// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transfer Order', {
	setup: function(frm){
		frm.set_query('picker', function(doc) {
			return {
				query: "golden.golden.doctype.employee_settings.employee_settings.employee_query",
				filters: { 'department': 'picker' }
			}
		});
		frm.set_query('receiver', function(doc) {
			return {
				query: "golden.golden.doctype.employee_settings.employee_settings.employee_query",
				filters: { 'department': 'receiver' }
			}
		});
	},
	refresh: function(frm) {
	},
});
frappe.ui.form.on('Transfer Order Item', {
	item_code: function(doc, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.item_code){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Item",
					filters:{
						name: d.item_code,
					}
				},
				callback: function (data) {
					frappe.model.set_value(cdt, cdn, "stock_uom", data.message.stock_uom);
					frappe.model.set_value(cdt, cdn, "transfer_uom", data.message.stock_uom);
					frappe.model.set_value(cdt, cdn, "to_location", data.message.default_warehouse);
				}
			})
		}
	},
	transfer_uom: function(doc, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.transfer_uom && d.item_code){
			return frappe.call({
				method: "golden.golden.doctype.transfer_order.transfer_order.get_uom_details",
				args: {
					item_code: d.item_code,
					uom: d.transfer_uom
				},
				callback: function(r) {
					if(r.message) {
						frappe.model.set_value(cdt, cdn, r.message);
					}
				}
			});
		}
	},
	batch: function(doc, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.batch){
			frappe.call({
				method: "golden.golden.doctype.transfer_order.transfer_order.get_qty_available",
				args:{
					item_code: d.item_code,
					batch: d.batch,
					warehouse: d.from_location
				},
				callback: function (r) {
					if(r.message) {
						frappe.model.set_value(cdt, cdn, r.message);
					}
				}
			})
		}else{
			frappe.model.set_value(cdt, cdn, "qty_available", "");
		}
	}
})
cur_frm.set_query("from_location", "items",  function (doc, cdt, cdn) {
	var c_doc= locals[cdt][cdn];
	return {
		filters: {
			'is_group': 0,
			'type': 'Location'
		}
	}
});
cur_frm.set_query("to_location", "items",  function (doc, cdt, cdn) {
	var c_doc= locals[cdt][cdn];
	return {
		filters: {
			'is_group': 0,
			'type': 'Location'
		}
	}
});
cur_frm.set_query("batch", "items",  function (doc, cdt, cdn) {
	var c_doc= locals[cdt][cdn];
	return {
		filters: {
			'item': c_doc.item_code
		}
	}
});
