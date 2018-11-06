// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Receive Order', {
	setup: function(frm){
		frm.set_query('accepted_location', function(doc) {
			return {
				filters: { 'is_group': 0 }
			}
		});
		frm.set_query("expedition", function (doc) {
			return {
				filters: {
					'buying': 1
				}
			}
		});
		frm.set_indicator_formatter('item_code',
			function(doc) {
				return (doc.qty == doc.si_qty) ? "green" : "blue"
			}
		)
	},
	onload: function(frm) {
		frm.set_query("item_code", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				query: "golden.golden.doctype.receive_order.receive_order.get_item_code",
			}
		});
		frm.set_query("purchase_order", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				query: "golden.golden.doctype.receive_order.receive_order.get_list_purchase_order",
				filters: {
					'item_code': row.item_code,
				}
			}
		});
		frm.set_query("uom", "items", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				query: "golden.golden.stock.uom_query",
				filters: { 'item_code': row.item_code }
			}
		});
	},
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 || frm.doc.__islocal) {
			frm.add_custom_button(__("Get Purchase Order"), function() {
				items = $.map( cur_frm.doc.items, function(item,idx) { return item.purchase_order } )
				added_items = items.join(",")
				erpnext.utils.map_current_doc({
					method: "golden.golden.doctype.receive_order.receive_order.get_purchase_order",
					source_doctype: "Purchase Order",
					target: frm,
					setters:  {
						company: frm.doc.company || undefined,
					},
					get_query_filters: {
						docstatus: 1,
						company: frm.doc.company,
						status: ["in", "To Receive and Bill, To Receive"],
						name: ["not in", added_items]
					}
				})
			});
		}
		if(frm.doc.docstatus == 0 || frm.doc.__islocal){
			frm.events.set_read_only(frm);
		}
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
});
frappe.ui.form.on('Receive Order Item', {
	purchase_order: function(doc, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.purchase_order){
			frappe.call({
				method: "golden.golden.doctype.receive_order.receive_order.get_po_detail",
				args:{
					po: d.purchase_order,
					item_code: d.item_code
				},
				callback: function (r) {
					if(r.message) {
						frappe.model.set_value(cdt, cdn, r.message);
					}
				}
			})
		}
	},
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
				}
			})
			// frappe.call({
			// 	method: "frappe.client.get",
			// 	args: {
			// 		doctype: "Purchase Order Item",
			// 		filters:{
			// 			item_code: d.item_code,
			// 			parent: d.purchase_order
			// 		}
			// 	},
			// 	callback: function (data) {
			// 		var qty = flt(data.message.qty) - flt(data.message.received_qty);
			// 		frappe.model.set_value(cdt, cdn, "purchase_order", data.message.parent);
			// 		frappe.model.set_value(cdt, cdn, "po_detail", data.message.name);
			// 		frappe.model.set_value(cdt, cdn, "qty", qty);
			// 		frappe.model.set_value(cdt, cdn, "uom", data.message.uom);
			// 		frappe.model.set_value(cdt, cdn, "conversion_factor", data.message.conversion_factor);
			// 	}
			// })
		}else{
			frappe.model.set_value(cdt, cdn, "stock_uom", "");
			frappe.model.set_value(cdt, cdn, "uom", "");
			frappe.model.set_value(cdt, cdn, "conversion_factor", "1");
		}
	},
	uom: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.uom){
			return frappe.call({
				method: "golden.golden.doctype.receive_order.receive_order.get_conversion_factor",
				args: {
					parent: d.item_code,
					uom: d.uom
				},
				callback: function (data) {
					if(data.message){
						frappe.model.set_value(cdt, cdn, data.message);
					}
				}
			})
		}
	}
})
// cur_frm.set_query("purchase_order", "items",  function (doc, cdt, cdn) {
// 	var c_doc= locals[cdt][cdn];
// 	return {
// 		query: "golden.golden.doctype.receive_order.receive_order.get_list_purchase_order",
// 		filters: {
// 			'item_code': c_doc.item_code,
// 		}
// 	}
// });
// cur_frm.set_query("item_code", "items",  function (doc, cdt, cdn) {
// 	var c_doc= locals[cdt][cdn];
// 	return {
// 		query: "golden.golden.doctype.receive_order.receive_order.get_item_code",
// 	}
// });
