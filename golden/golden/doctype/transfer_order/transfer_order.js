// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transfer Order', {
	refresh: function(frm) {
/*
		if(frm.doc.docstatus == 1 && frm.doc.status == "Submitted") {
			cur_frm.add_custom_button(__('Material Transfer'), cur_frm.cscript['Material Transfer'], __("Make"));
			cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
		}
		*/
	}
});
/*
cur_frm.cscript['Material Transfer'] = function() {
	frappe.model.open_mapped_doc({
		method: "golden.golden.stock.make_material_transfer",
		frm: cur_frm
	})
}
*/
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
