// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warehouse Routing', {
	refresh: function(frm) {

	},
	onload: function(frm) {
		frm.set_query('warehouse', function(doc) {
			return {
				filters: {
					"is_group": 1,
					"type": "Warehouse"
				}
			}
		})
		frm.set_query("warehouse", "details", function(doc, cdt, cdn) {
			var row = locals[cdt][cdn];
			return {
				filters: {
					"is_group": 1,
					"type": "Warehouse"
				}
			}
		});
	},
});
