frappe.ui.form.on('Delivery Note', {
	 	refresh: function(frm) {
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
