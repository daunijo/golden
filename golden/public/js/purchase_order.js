frappe.ui.form.on('Purchase Order', {
	 	refresh: function(frm) {
			frm.set_value("schedule_date", frm.doc.transaction_date);
		},

     transaction_date: function(frm){
       frm.set_value("schedule_date", frm.doc.transaction_date);
     },
})
