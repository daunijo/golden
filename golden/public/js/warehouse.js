frappe.ui.form.on('Warehouse', {
	refresh: function(frm) {
		switch(frm.doc.type) {
			case 'Location' :
				frm.add_custom_button(__("Stock Position"), function() {
					frappe.set_route("query-report", "Stock Position", {"location": frm.doc.name});
				});break;
			case 'Section' :
				frm.add_custom_button(__("Stock Position"), function() {
						frappe.set_route("query-report", "Stock Position", {"section": frm.doc.name});
				}); break;

			default :
				frm.add_custom_button(__("Stock Position"), function() {
					frappe.set_route("query-report", "Stock Position", {"warehouse": frm.doc.name});
				}); break;
			}

		frm.fields_dict['parent_warehouse_rss'].get_query = function(doc) {
			return {
				filters: {
					"is_group": 1,
					"type": "Warehouse",
				}
			}
		},
		frm.fields_dict['parent_warehouse'].get_query = function(doc) {
			return {
				filters: {
					"is_group": 1,
					"old_parent": ""
				}
			}
		}
	},
	setup: function(frm){
		frm.set_query("parent_section_rss", function(doc) {
			return {
				filters: {
					'is_group': 1,
					'type': 'Section'
				}
			}
		});
	},
	onload: function(frm){
		frm.set_df_property("parent_warehouse", "read_only", 1);
		frm.set_df_property("parent_warehouse", "hidden", 1);
		if(frm.doc.type == "Location"){
			frm.set_df_property("parent_warehouse_rss", "read_only", 1);
		}
		frm.toggle_reqd(['parent_warehouse_rss', 'parent_section_rss'], false);
		frm.set_query("parent_section_rss",  function (doc) {
				return {
		        filters: [
		            ['old_parent', '=', frm.doc.parent_warehouse_rss]
		        ],
				}
		});
	},
	parent_warehouse_rss: function(frm){
		if(frm.doc.type == "Section"){
			frm.set_value("parent_warehouse", frm.doc.parent_warehouse_rss);
		}
	},
	type: function(frm){
		if(cur_frm.doc.type == 'Warehouse' || cur_frm.doc.type == 'Section'){
			frm.set_value("is_group", 1);
		}else {
			frm.set_value("is_group", 0);
		}
		if(frm.doc.type == "Section"){
			frm.set_value("parent_warehouse_rss", undefined);
			frm.set_value("parent_section_rss", undefined);
			frm.toggle_reqd('parent_warehouse_rss', true);
			frm.toggle_reqd('parent_section_rss', false);
			frm.set_df_property("parent_warehouse_rss", "read_only", 0);
			frm.refresh_fields();
		}else if(frm.doc.type == "Location"){
			frm.toggle_reqd(['parent_warehouse_rss', 'parent_section_rss'], true);
			frm.set_df_property("parent_warehouse_rss", "read_only", 1);
			frm.refresh_fields();
		}else{
			frm.toggle_reqd(['parent_warehouse_rss', 'parent_section_rss'], false);
		}
	},
	parent_section_rss: function(frm){
		frm.set_value("parent_warehouse", frm.doc.parent_section_rss);
		if(frm.doc.parent_section_rss){
			frappe.call({
				method: "frappe.client.get",
				args:{
					doctype: "Warehouse",
					filters:{
						name: frm.doc.parent_section_rss
					}
				},
				callback: function(data){
					frm.set_value("parent_warehouse_rss", data.message.parent_warehouse);
				}
			});
		}
	},

})
