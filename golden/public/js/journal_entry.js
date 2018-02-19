frappe.ui.form.on("Journal Entry", {
	setup: function(frm) {
		frm.get_field('accounts').grid.editable_fields = [
			{fieldname: 'account', columns: 3},
			{fieldname: 'cost_center', columns: 3},
			{fieldname: 'debit_in_account_currency', columns: 2},
			{fieldname: 'credit_in_account_currency', columns: 2}
		];
	},
})
