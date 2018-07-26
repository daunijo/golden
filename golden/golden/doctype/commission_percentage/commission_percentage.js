// Copyright (c) 2018, RSS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Commission Percentage', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 0 || frm.doc.__islocal){
			frm.events.set_read_only(frm);
		}
	},
	set_posting_time: function(frm){
		frm.events.set_read_only(frm);
	},
	set_read_only: function(frm){
		if(frm.doc.set_posting_time == 1){
			frm.set_df_property("posting_date", "read_only", false);
			frm.set_df_property("posting_time", "read_only", false);
		}else{
			frm.set_df_property("posting_date", "read_only", true);
			frm.set_df_property("posting_time", "read_only", true);
		}
	},
	commission_type: function(frm){
		if(frm.doc.commission_type == "SEL"){
			frm.clear_table("collects");
		}else if(frm.doc.commission_type == "RETURN"){
			frm.clear_table("collects");
		}else{
			frm.clear_table("details");
		}
	},
	sales: function(frm){
		if(frm.doc.sales){
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Employee",
					filters:{
						name: frm.doc.sales,
					}
				},
				callback: function (data) {
					if(data.message){
						frm.set_value("sales_name", data.message.employee_name);
					}
				}
			})
		}else{
			frm.set_value("sales_name", "");
		}
	}
});
