// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Delivery Keeptrack', {
	refresh: function(frm) {

	},
	refresh: function() {
		if(cur_frm.doc.docstatus == 0 || cur_frm.doc.__islocal){
			cur_frm.add_custom_button(__("Packing List"), function() {
				erpnext.utils.map_current_doc({
					method: "golden.golden.stock.get_packing_list",
					source_doctype: "Packing",
					target: cur_frm,
					setters:  {
						company: cur_frm.doc.company || undefined,
						//customer: undefined,
					},
					get_query_filters: {
						docstatus: 1,
					}
				})
			}, __("Get details from"));
		}
	},
});
