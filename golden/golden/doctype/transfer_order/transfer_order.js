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
