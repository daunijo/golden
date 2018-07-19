// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Region', {
	setup: function(frm) {
		frm.set_query('city', function(doc) {
			return {
				filters: { 'disabled': 0 }
			}
		});
	}
});
