frappe.ui.form.on('Stock Reconciliation', {
	 	refresh: function(frm) {
			frm.fields_dict['items'].grid.get_field("default_gudang").get_query = function(frm,cdt,cdn) {
				var d = locals[cdt][cdn];
				return {
					filters: {
						"is_group": 1,
						"type": "warehouse",
					}
				}
			},
			frm.fields_dict['items'].grid.get_field("default_section").get_query = function(frm,cdt,cdn) {
				var d = locals[cdt][cdn];
				return {
					filters: {
						"is_group": 1,
						"type": "section",
						"parent_warehouse": d.default_gudang
					}
				}
			},
			frm.fields_dict['items'].grid.get_field("default_location").get_query = function(frm,cdt,cdn) {
				var d = locals[cdt][cdn];
				return {
					filters: {
						"is_group": 0,
						"type": "location",
						"parent_warehouse": d.default_section
					}
				}
			},

			frm.fields_dict['items'].grid.get_field("warehouse").get_query = function(frm,cdt,cdn) {
				var d = locals[cdt][cdn];
				return {
					filters: {
						"is_group": 0,
						"type": "location",
						"parent_warehouse": d.default_section
					}
				}
			},

      frm.trigger("toggle_fields");
  		if(frm.doc.docstatus == 1) {
  			frm.add_custom_button(__('Stock Card'), function() {
  				frappe.route_options = {
  					voucher_no: frm.doc.name,
  					from_date: frm.doc.posting_date,
  					to_date: frm.doc.posting_date,
  					company: frm.doc.company,
  					group_by_voucher: false
  				};
  				frappe.set_route("query-report", "Stock Card");
  			}, __("View"));
  		}
		},
})
