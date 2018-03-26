frappe.ui.form.on('Item', {
	 	refresh: function(frm) {
      if(frm.doc.is_stock_item) {
  			frm.add_custom_button(__("Stock Card"), function() {
  				frappe.route_options = {
  					"item_code": frm.doc.name
  				}
  				frappe.set_route("query-report", "Stock Card");
  			}, __("View"));
  			frm.add_custom_button(__("Stock Position"), function() {
  				frappe.route_options = {
  					"item_code": frm.doc.name
  				}
  				frappe.set_route("query-report", "Stock Position");
  			}, __("View"));
  		}
		},
})
