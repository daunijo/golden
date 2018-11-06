cur_frm.set_query("default_gudang", "items",  function (doc, cdt, cdn) {
	var c_doc= locals[cdt][cdn];
	return {
	//	query: "golden.golden.stock.default_gudang"
		filters: {
			'is_group': 1,
			'type': 'Warehouse',
			'disabled': 0
		}
	}
});
/*
cur_frm.set_query("default_section", "items",  function (doc, cdt, cdn) {
	var c_doc= locals[cdt][cdn];
	return {
		filters: {
			'is_group': 1,
			'type': 'Section',
			'parent': c_doc.default_gudang
		}
	}
});
*/
frappe.ui.form.on('Stock Reconciliation Item', {
	default_location: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "warehouse", d.default_location);
		frappe.call({
			method: "frappe.client.get",
			args:{
				doctype: "Warehouse",
				filters:{
					name: d.default_location
				}
			},
			callback: function(data){
				frappe.model.set_value(cdt, cdn, "default_section", data.message.parent_warehouse);
			}
		});
	},
	default_section: function(frm, cdt, cdn){
		row = locals[cdt][cdn];
		frappe.call({
			method: "frappe.client.get",
			args:{
				doctype: "Warehouse",
				filters:{
					name: row.default_section
				}
			},
			callback: function(data){
				frappe.model.set_value(cdt, cdn, "default_gudang", data.message.parent_warehouse);
			}
		});
	}
})
