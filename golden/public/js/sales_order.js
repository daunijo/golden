frappe.ui.form.on('Sales Order', {
	 	refresh: function(frm) {
			frm.set_value("delivery_date", frm.doc.transaction_date);
		},

     transaction_date: function(frm){
       frm.set_value("delivery_date", frm.doc.transaction_date);
     },
})
