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

     parent_warehouse_rss: function(frm){
       frm.set_value("parent_warehouse", frm.doc.parent_warehouse_rss);
     },

	   type: function(frm){
       if(cur_frm.doc.type == 'Warehouse' || cur_frm.doc.type == 'Section'){
		     frm.set_value("is_group", 1);
       }else {
         frm.set_value("is_group", 0);
       }
     },

     parent_section_rss: function(frm){
   		frm.set_value("parent_warehouse", frm.doc.parent_section_rss);
   	},

})

cur_frm.set_query("parent_section_rss",  function (frm) {
		return {
        filters: [
            ['old_parent', '=', cur_frm.doc.parent_warehouse_rss]
        ],
		}
});
