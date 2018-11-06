frappe.ui.form.on('Item', {
	refresh: function(frm) {
    if(frm.doc.is_stock_item) {
  		frm.add_custom_button(__("Stock Card"), function() {
  			frappe.route_options = {
  				"item_code": frm.doc.name
  			}
  			frappe.set_route("query-report", "Stock Card");
  		}, __("View"));
  		frm.add_custom_button(__("Stock Position"), function() {
  			frappe.route_options = {
  				"item_code": frm.doc.name
  			}
  			frappe.set_route("query-report", "Stock Position");
  		}, __("View"));
  	}
	},
	item_group: function(frm){
		if(frm.doc.item_group){
			frappe.call({
				method: "frappe.client.get",
				args:{
					doctype: "Item Group",
					filters:{
						name: frm.doc.item_group
					}
				},
				callback: function(data){
					frm.set_value("default_location", data.message.default_location);
				}
			});
		}
	},
	default_location: function(frm){
		frm.set_value("default_warehouse", frm.doc.default_location);
		frappe.call({
			method: "frappe.client.get",
			args:{
				doctype: "Warehouse",
				filters:{
					name: frm.doc.default_location
				}
			},
			callback: function(data){
				frm.set_value("default_section", data.message.parent_warehouse);
			}
		});
	},
	default_section: function(frm){
		frappe.call({
			method: "frappe.client.get",
			args:{
				doctype: "Warehouse",
				filters:{
					name: frm.doc.default_section
				}
			},
			callback: function(data){
				frm.set_value("default_gudang", data.message.parent_warehouse);
			}
		});
	}
})
cur_frm.set_query("default_gudang", function(frm) {
	return {
		filters: {
			'is_group': 1,
			'type': 'Warehouse'
		}
	}
});
cur_frm.set_query("default_section", function(frm) {
	return {
		filters: {
			'is_group': 1,
			'type': 'Section',
			'parent': frm.doc.default_gudang
		}
	}
});
cur_frm.set_query("default_location", function(frm) {
	return {
		filters: {
			'is_group': 0,
			'type': 'Location'
		}
	}
});
