// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Settings', {
	refresh: function(frm) {

	}
});
frappe.ui.form.on('Employee Settings Detail', {
	employee: function(doc, cdt, cdn) {
		var d = locals[cdt][cdn];
		if(d.employee){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Employee",
					filters:{
						name: d.employee,
					}
				},
				callback: function (data) {
					frappe.model.set_value(cdt, cdn, "department", data.message.department);
				}
			})
		}
	}
});
