// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('City', {
	refresh: function(frm) {
		frm.set_query('region', function(doc) {
			return {
				filters: { 'disabled': 0 }
			}
		});
	}
});
